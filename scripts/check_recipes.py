#!/usr/bin/env python3
"""Validate the recipe library and scan for suspicious content.

Usage:
    python scripts/check_recipes.py [--root DIR]
    python scripts/check_recipes.py --scan FILE...

Exit code is 1 if any error was found, else 0. Warnings never fail the run.
"""
from __future__ import annotations

import argparse
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

README_LINK_RE = re.compile(
    r"\(\.?/?skills/sargento-rea/recipes/([a-z0-9-]+)\.md(?:#[^)]*)?\)"
)

SUSPICIOUS = (
    (re.compile("[​-‏‪-‮⁠-⁤⁦-⁩﻿]"),
     "invisible or bidirectional control character"),
    (re.compile(r"\b(curl|wget)\b[^\n|]*\|\s*(sudo\s+)?(ba|z)?sh\b"),
     "download piped into a shell"),
    (re.compile(r"\biex\b\s*\(?\s*(irm|iwr|invoke-restmethod|invoke-webrequest)\b",
                re.IGNORECASE),
     "PowerShell download-and-execute"),
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
    if "learned_from" in data:
        lf = data["learned_from"]
        if not isinstance(lf, list) or not all(isinstance(i, dict) for i in lf):
            err("'learned_from' must be a list of name/url entries")
        else:
            for i, item in enumerate(lf, 1):
                if not item.get("name"):
                    err(f"learned_from entry {i} is missing 'name'")
                if not item.get("url", "").startswith("https://"):
                    err(f"learned_from entry {i} needs an https:// 'url'")
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

    seen: set[Path] = set()
    for pattern in SCAN_GLOBS:
        for file in sorted(root.glob(pattern)):
            if file in seen or file in undecodable or not file.is_file():
                continue
            seen.add(file)
            text, problem = _read(file)
            if problem:
                findings.append(Finding(file.relative_to(root).as_posix(), "error",
                                        problem.message))
                continue
            findings.extend(scan_suspicious(file.relative_to(root).as_posix(), text))
    return findings


def _print(findings: list[Finding]) -> None:
    for f in findings:
        print(f"{f.level.upper()} {f.path}: {f.message}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check the Sargento REA recipe library.")
    parser.add_argument("--root", default=".", help="repository root (default: .)")
    parser.add_argument("--scan", nargs="+", metavar="FILE",
                        help="scan arbitrary files for suspicious content (warnings only)")
    args = parser.parse_args(argv)

    findings: list[Finding] = []
    if args.scan:
        for name in args.scan:
            text, problem = _read(Path(name))
            if problem:
                findings.append(problem)
            else:
                findings.extend(scan_suspicious(name, text))
    else:
        findings = check_repo(Path(args.root))
    _print(findings)
    return 1 if any(f.level == "error" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
