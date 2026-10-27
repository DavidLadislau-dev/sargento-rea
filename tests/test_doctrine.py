import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_recipes as cr  # noqa: E402

SKILL_DIR = ROOT / "skills" / "sargento-rea"
DOCTRINE = (
    "study-mission",
    "build-mission",
    "squad-herdr",
    "squad-subagents",
    "review-contribution",
)
STUDY_LAYOUT = (
    "orders/",
    "reports/",
    "ledger/facts.md",
    "ledger/unknowns.md",
    "raw/",
    "README.md",
)
BRIEF_PARTS = ("what it is for", "what changes", "benefits", "dangers", "recommendation")


def read(path: Path) -> str:
    return path.read_bytes().decode("utf-8").replace("\r\n", "\n")


def doctrine(name: str) -> str:
    return read(SKILL_DIR / "doctrine" / f"{name}.md")


def section(text: str, word: str) -> str:
    """Text of the first heading (any level) containing `word`, up to the next heading."""
    match = re.search(rf"^#+ [^\n]*{re.escape(word)}[^\n]*$", text, re.IGNORECASE | re.MULTILINE)
    if match is None:
        raise AssertionError(f"no heading containing {word!r}")
    rest = text[match.end():]
    nxt = re.search(r"^#+ ", rest, re.MULTILINE)
    return rest[:nxt.start()] if nxt else rest


class DoctrineTests(unittest.TestCase):
    def test_all_doctrine_files_exist_and_are_linked(self):
        skill = read(SKILL_DIR / "SKILL.md")
        for name in DOCTRINE:
            rel = f"doctrine/{name}.md"
            with self.subTest(file=rel):
                self.assertTrue((SKILL_DIR / rel).is_file(), f"{rel} is missing")
                self.assertIn(f"]({rel})", skill, f"SKILL.md does not link {rel}")

    def test_doctrine_has_no_suspicious_content(self):
        for name in DOCTRINE:
            with self.subTest(file=name):
                self.assertEqual(cr.scan_suspicious(name, doctrine(name)), [])

    def test_review_doctrine_core_rules(self):
        text = doctrine("review-contribution")
        for needle in ("gh pr diff", "git diff main...", "check_recipes.py --scan"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)
        lower = text.lower()
        for part in BRIEF_PARTS:
            with self.subTest(part=part):
                self.assertIn(part, lower)
        self.assertIn("never check out or run pr code", lower)
        self.assertIn("untrusted", lower)

    def test_herdr_doctrine_trust_rule(self):
        text = doctrine("squad-herdr")
        trust = section(text, "trust")
        for needle in (".claude/settings.json", ".mcp.json", "raw/"):
            with self.subTest(needle=needle):
                self.assertIn(needle, trust)
        self.assertIn("`!`", section(text, "auto mode"))

    def test_study_doctrine_layout(self):
        text = doctrine("study-mission")
        for path in STUDY_LAYOUT:
            with self.subTest(path=path):
                self.assertIn(f"`{path}`", text)
        self.assertIn('"resume here"', text)
        self.assertIn("-I", text)

    def test_build_doctrine_spec_step(self):
        text = doctrine("build-mission")
        for skill in ("brainstorming", "writing-plans"):
            with self.subTest(skill=skill):
                self.assertIn(f"`{skill}`", text)


if __name__ == "__main__":
    unittest.main()
