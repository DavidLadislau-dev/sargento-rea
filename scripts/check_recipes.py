#!/usr/bin/env python3
"""Validate the recipe library and scan for suspicious content.

Usage:
    python scripts/check_recipes.py [--root DIR]
    python scripts/check_recipes.py --scan FILE...

Exit code is 1 if any error was found, else 0. Warnings never fail the run.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

RECIPES_DIR = Path("skills/sargento-rea/recipes")
REQUIRED_KEYS = (
    "id", "title", "summary", "mission", "needs", "tools", "authors",
    "learned_from", "status",
)
REQUIRED_HEADINGS = (
    "## When to use",
    "## What you need",
    "## Steps",
    "## How the Sargento splits the work",
    "## How to prove it worked",
    "## Sources and credits",
)
MISSIONS = {"study", "build"}
STATUSES = {"proven-upstream", "tested", "draft"}
SCAN_GLOBS = ("skills/**/*.md", ".claude-plugin/*.json")
# Directories that never ship: pruned from the whole-repo markdown walk so a
# filesystem scan matches a fresh clone, and a working copy's local-only
# scratch dirs (these mirror .gitignore) raise no false findings.
PRUNE_DIRS = frozenset({
    ".git", "docs", ".superpowers", ".claude", "raw",
    "__pycache__", "node_modules", ".pytest_cache",
})

README_LINK_RE = re.compile(
    r"\(\.?/?skills/sargento-rea/recipes/([a-z0-9-]+)\.md(?:#[^)]*)?\)"
)
# owner/repo of a github.com link; whatever follows (/blob/..., /pull/N,
# /issues/N) is ignored. The lookbehind keeps gist.github.com and the like out.
GITHUB_REPO_RE = re.compile(
    r"(?<![\w.-])(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9-]+)/([A-Za-z0-9._-]+)"
)
SOURCES_HEADING = "## Sources and credits"

# A pipe into `sudo`, with any flags, before the program that runs the download.
_SUDO = r"(sudo\b[^\n|]*?\s)?"
SUSPICIOUS = (
    (re.compile(r"[\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u2069\ufeff]"),
     "invisible or bidirectional control character"),
    (re.compile(r"\b(curl|wget)\b[^\n|]*\|\s*" + _SUDO + r"(ba|z)?sh\b"),
     "download piped into a shell"),
    (re.compile(r"\b(curl|wget)\b[^\n|]*\|\s*" + _SUDO + r"(python[0-9.]*|perl|ruby|node)\b"),
     "download piped into an interpreter"),
    (re.compile(r"[<$]\(\s*(curl|wget)\b"),
     "download inside process or command substitution"),
    (re.compile(r"\biex\b\s*\(?\s*(irm|iwr|invoke-restmethod|invoke-webrequest)\b",
                re.IGNORECASE),
     "PowerShell download-and-execute"),
    (re.compile(r"\b(irm|iwr|invoke-restmethod|invoke-webrequest)\b[^\n]*\|\s*iex\b",
                re.IGNORECASE),
     "PowerShell download piped into iex"),
    (re.compile(r"\binvoke-expression\b", re.IGNORECASE), "Invoke-Expression call"),
    (re.compile(r"\bDownload(String|File|Data)\b"), "Download* call"),
    (re.compile(r"\bFromBase64String\b"), "FromBase64String call"),
    (re.compile(r"[A-Za-z0-9+/]{120,}={0,2}"), "long base64-like blob"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "hard-coded IP address"),
    (re.compile(r"<!--"), "HTML comment"),
)


@dataclass(frozen=True)
class Finding:
    path: str
    level: str  # "error" | "warning"
    message: str


class FrontmatterError(ValueError):
    pass


def _strip_value(raw: str) -> str:
    value = re.sub(r"\s+#.*$", "", raw).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value


def _split_kv(line: str, lineno: int) -> tuple[str, str]:
    if ":" not in line:
        raise FrontmatterError(f"line {lineno}: expected 'key: value', got {line.strip()!r}")
    key, _, rest = line.partition(":")
    key = key.strip()
    if not key:
        raise FrontmatterError(f"line {lineno}: empty key")
    return key, rest


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse the restricted frontmatter grammar. Returns (data, body)."""
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0] != "---":
        raise FrontmatterError("line 1: file must start with a '---' line")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise FrontmatterError("line 1: frontmatter is never closed with '---'") from None

    data: dict = {}
    current_list_key: str | None = None
    items: list[dict[str, str]] = []
    for idx in range(1, end):
        lineno = idx + 1
        line = lines[idx]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line[0] in " \t":
            if current_list_key is None:
                raise FrontmatterError(f"line {lineno}: unexpected indented line")
            if stripped.startswith("- "):
                key, rest = _split_kv(stripped[2:], lineno)
                items.append({key: _strip_value(rest)})
            else:
                if not items:
                    raise FrontmatterError(f"line {lineno}: list item must start with '- '")
                key, rest = _split_kv(stripped, lineno)
                items[-1][key] = _strip_value(rest)
            continue
        if current_list_key is not None:
            data[current_list_key] = items if items else ""
            current_list_key = None
            items = []
        key, rest = _split_kv(line, lineno)
        if key in data:
            raise FrontmatterError(f"line {lineno}: duplicate key {key!r}")
        value = _strip_value(rest)
        if value == "":
            current_list_key = key
            items = []
        elif value.startswith("["):
            if not value.endswith("]"):
                raise FrontmatterError(f"line {lineno}: unterminated list")
            inner = value[1:-1].strip()
            data[key] = [_strip_value(p) for p in inner.split(",")] if inner else []
        else:
            data[key] = value
    if current_list_key is not None:
        data[current_list_key] = items if items else ""
    return data, "\n".join(lines[end + 1:])


def _headings(body: str) -> list[str]:
    found: list[str] = []
    in_fence = False
    for line in body.split("\n"):
        if line.startswith("```") or line.startswith("~~~"):
            in_fence = not in_fence
            continue
        if not in_fence and line.startswith("## "):
            found.append(line.rstrip())
    return found


def _section(body: str, heading: str) -> str:
    """Text under `heading` (a '## ' line outside code fences), up to the next one."""
    out: list[str] = []
    inside = in_fence = False
    for line in body.split("\n"):
        if line.startswith("```") or line.startswith("~~~"):
            in_fence = not in_fence
        elif not in_fence and line.startswith("## "):
            inside = line.rstrip() == heading
            continue
        if inside:
            out.append(line)
    return "\n".join(out)


def github_repos(text: str) -> dict[str, str]:
    """Map lower-cased 'owner/repo' to its first spelling, for every github.com link."""
    found: dict[str, str] = {}
    for owner, repo in GITHUB_REPO_RE.findall(text):
        repo = repo.rstrip(".")
        if repo.endswith(".git"):
            repo = repo[:-4]
        if repo:
            found.setdefault(f"{owner}/{repo}".lower(), f"{owner}/{repo}")
    return found


def check_recipe(path: Path, text: str) -> list[Finding]:
    name = path.as_posix()
    out: list[Finding] = []

    def err(msg: str) -> None:
        out.append(Finding(name, "error", msg))

    try:
        data, body = parse_frontmatter(text)
    except FrontmatterError as exc:
        return [Finding(name, "error", f"frontmatter: {exc}")]

    for key in REQUIRED_KEYS:
        if key not in data:
            err(f"missing required key '{key}'")
    for key in ("id", "title", "summary", "mission", "status"):
        if key in data and (not isinstance(data[key], str) or not data[key]):
            err(f"'{key}' must be a non-empty string")
    for key in ("needs", "tools", "authors"):
        if key in data and not isinstance(data[key], list):
            err(f"'{key}' must be a list")
    if isinstance(data.get("authors"), list) and not data["authors"]:
        err("'authors' must not be empty")
    credited: set[str] | None = None
    if "learned_from" in data:
        lf = data["learned_from"]
        if not isinstance(lf, list) or not all(isinstance(i, dict) for i in lf):
            err("'learned_from' must be a list of name/url entries")
        else:
            credited = set()
            for i, item in enumerate(lf, 1):
                if not item.get("name"):
                    err(f"learned_from entry {i} is missing 'name'")
                if not item.get("url", "").startswith("https://"):
                    err(f"learned_from entry {i} needs an https:// 'url'")
                credited.update(github_repos(item.get("url", "")))
    if isinstance(data.get("id"), str) and data["id"] and data["id"] != path.stem:
        err(f"'id' ({data['id']}) must equal the file name ({path.stem})")
    if isinstance(data.get("mission"), str) and data["mission"] \
            and data["mission"] not in MISSIONS:
        err(f"'mission' must be one of {sorted(MISSIONS)}, got {data['mission']!r}")
    if isinstance(data.get("status"), str) and data["status"] \
            and data["status"] not in STATUSES:
        err(f"'status' must be one of {sorted(STATUSES)}, got {data['status']!r}")

    headings = _headings(body)
    positions = []
    for heading in REQUIRED_HEADINGS:
        count = headings.count(heading)
        if count == 0:
            err(f"missing heading '{heading}'")
        elif count > 1:
            err(f"heading '{heading}' appears {count} times, expected once")
        else:
            positions.append(headings.index(heading))
    if positions != sorted(positions):
        err("required headings are out of order")

    if credited is not None and SOURCES_HEADING in headings:
        cited = github_repos(_section(body, SOURCES_HEADING))
        for key, repo in cited.items():
            if key not in credited:
                err(f"'{SOURCES_HEADING}' cites github.com/{repo}, "
                    "which no 'learned_from' url credits")
    return out


def scan_suspicious(path: str, text: str) -> list[Finding]:
    out: list[Finding] = []
    for lineno, line in enumerate(text.replace("\r\n", "\n").split("\n"), 1):
        for regex, label in SUSPICIOUS:
            if regex.search(line):
                out.append(Finding(path, "warning", f"line {lineno}: {label}"))
    return out


def readme_recipe_ids(readme_text: str) -> list[str]:
    return README_LINK_RE.findall(readme_text)


def _read(path: Path) -> tuple[str | None, Finding | None]:
    try:
        text = path.read_bytes().decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        return None, Finding(path.as_posix(), "error", f"not valid UTF-8: {exc}")
    return text.replace("\r\n", "\n"), None


def scan_file(name: str) -> list[Finding]:
    """`--scan` one file. Bad UTF-8 is replaced and reported per line, so one
    bad byte cannot hide the rest of the file; an unreadable file is an error."""
    try:
        data = Path(name).read_bytes()
    except OSError as exc:
        return [Finding(name, "error", f"could not read: {exc.strerror or exc}")]
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    out: list[Finding] = []
    lines: list[str] = []
    # 0x0A never occurs inside a multi-byte UTF-8 sequence, so splitting the
    # bytes first keeps the line numbers of scan_suspicious.
    for lineno, raw in enumerate(data.split(b"\n"), 1):
        try:
            lines.append(raw.decode("utf-8"))
        except UnicodeDecodeError:
            lines.append(raw.decode("utf-8", errors="replace"))
            out.append(Finding(name, "warning", f"line {lineno}: invalid UTF-8 bytes"))
    return out + scan_suspicious(name, "\n".join(lines))


def _iter_markdown(root: Path):
    """Every `.md` file under root, with PRUNE_DIRS pruned from the walk."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in PRUNE_DIRS]
        for name in filenames:
            if name.endswith(".md"):
                yield Path(dirpath) / name


def _markdown_location_ok(rel: str) -> bool:
    """A committed markdown file may live only in the skill tree, the two root
    docs, or `.github/`. Anything else gets a human's eye before merge."""
    if rel in ("README.md", "CONTRIBUTING.md"):
        return True
    return rel.startswith("skills/sargento-rea/") or rel.startswith(".github/")


def check_repo(root: Path) -> list[Finding]:
    root = Path(root)
    findings: list[Finding] = []
    undecodable: set[Path] = set()

    recipes = sorted((root / RECIPES_DIR).glob("*.md")) if (root / RECIPES_DIR).is_dir() else []
    if not recipes:
        findings.append(Finding(RECIPES_DIR.as_posix(), "error",
                                f"no recipes found in {RECIPES_DIR.as_posix()}"))
    for recipe in recipes:
        text, problem = _read(recipe)
        rel = recipe.relative_to(root)
        if problem:
            findings.append(Finding(rel.as_posix(), "error", problem.message))
            undecodable.add(recipe)
            continue
        findings.extend(check_recipe(rel, text))

    readme = root / "README.md"
    if recipes:
        text, problem = _read(readme) if readme.is_file() else (None, None)
        if problem:
            findings.append(problem)
        elif text is None:
            findings.append(Finding("README.md", "error", "README.md not found"))
        else:
            listed = set(readme_recipe_ids(text))
            on_disk = {r.stem for r in recipes}
            for rid in sorted(on_disk - listed):
                findings.append(Finding("README.md", "error",
                                        f"recipe '{rid}' is missing from the README table"))
            for rid in sorted(listed - on_disk):
                findings.append(Finding("README.md", "error",
                                        f"README lists '{rid}' but no recipe file exists"))

    # Every markdown file in the repo, not just the skill tree: a file outside
    # the allowed locations is an error (it escapes the recipe, README and
    # template checks), and every markdown file is scanned for suspicious
    # content so nothing hides by sitting in an unscanned folder.
    for md in sorted(_iter_markdown(root)):
        if not md.is_file():
            continue
        rel = md.relative_to(root).as_posix()
        if not _markdown_location_ok(rel):
            findings.append(Finding(
                rel, "error",
                "markdown outside the skill, README or CONTRIBUTING; "
                "a recipe belongs in skills/sargento-rea/recipes/"))
        if md in undecodable:
            continue  # its UTF-8 error is already recorded
        text, problem = _read(md)
        if problem:
            findings.append(Finding(rel, "error", problem.message))
            continue
        findings.extend(scan_suspicious(rel, text))

    for file in sorted(root.glob(".claude-plugin/*.json")):
        if not file.is_file():
            continue
        rel = file.relative_to(root).as_posix()
        text, problem = _read(file)
        if problem:
            findings.append(Finding(rel, "error", problem.message))
            continue
        findings.extend(scan_suspicious(rel, text))
    return findings


def _print(findings: list[Finding]) -> None:
    for f in findings:
        print(f"{f.level.upper()} {f.path}: {f.message}")


def main(argv: list[str] | None = None) -> int:
    # A Windows console or a pipe may use a narrow code page; escape what it
    # cannot encode instead of crashing on a recipe's or a diff's characters.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(description="Check the Sargento REA recipe library.")
    parser.add_argument("--root", default=".", help="repository root (default: .)")
    parser.add_argument("--scan", nargs="+", metavar="FILE",
                        help="scan arbitrary files for suspicious content (warnings; an "
                             "unreadable file is an error)")
    args = parser.parse_args(argv)

    findings: list[Finding] = []
    if args.scan:
        for name in args.scan:
            findings.extend(scan_file(name))
    else:
        findings = check_repo(Path(args.root))
    _print(findings)
    return 1 if any(f.level == "error" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
