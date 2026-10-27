import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_recipes as cr  # noqa: E402

PLUGIN_DIR = ROOT / ".claude-plugin"
SKILL_DIR = ROOT / "skills" / "sargento-rea"
SKILL_MD = SKILL_DIR / "SKILL.md"
TEMPLATES = SKILL_DIR / "templates"

OVERLAY_HEADINGS = (
    "## About me",
    "## My rules",
    "## My machine",
    "## My tools",
    "## My workflow",
    "## My stack",
    "## Missions",
)
CLOSING_LINE = "finish with: what you did, files, tests run, open items"


def read(path: Path) -> str:
    return path.read_bytes().decode("utf-8").replace("\r\n", "\n")


def sections(text: str) -> dict[str, list[str]]:
    """Map each '## ' heading to the lines under it, up to the next '## '."""
    out: dict[str, list[str]] = {}
    current = None
    for line in text.split("\n"):
        if line.startswith("## "):
            current = line.rstrip()
            out[current] = []
        elif current is not None:
            out[current].append(line)
    return out


class ManifestTests(unittest.TestCase):
    def test_manifests_agree(self):
        plugin = json.loads(read(PLUGIN_DIR / "plugin.json"))
        market = json.loads(read(PLUGIN_DIR / "marketplace.json"))

        self.assertEqual(plugin["name"], "sargento-rea")
        self.assertEqual(plugin["version"], "0.1.0")
        self.assertEqual(plugin["license"], "MIT")

        self.assertEqual(market["name"], "sargento-rea")
        self.assertEqual(len(market["plugins"]), 1)
        entry = market["plugins"][0]
        self.assertEqual(entry["name"], plugin["name"])
        self.assertEqual(entry["version"], plugin["version"])
        self.assertEqual(entry["source"], "./")


class TemplateTests(unittest.TestCase):
    def test_recipe_template_matches_checker(self):
        text = read(TEMPLATES / "recipe.md")
        data, body = cr.parse_frontmatter(text)
        self.assertEqual(sorted(data), sorted(cr.REQUIRED_KEYS))

        headings = cr._headings(body)
        required = [h for h in headings if h in cr.REQUIRED_HEADINGS]
        self.assertEqual(required, list(cr.REQUIRED_HEADINGS))

        # A contributor who copies the template to <id>.md starts from a
        # file the checker accepts.
        self.assertEqual(cr.check_recipe(Path(f"{data['id']}.md"), text), [])

    def test_overlay_template_sections(self):
        text = read(TEMPLATES / "sargento.local.example.md")
        found = sections(text)
        for heading in OVERLAY_HEADINGS:
            with self.subTest(heading=heading):
                self.assertIn(heading, found)
                examples = [ln for ln in found[heading] if ln.startswith("> Example: ")]
                self.assertEqual(len(examples), 1, f"{heading} needs one '> Example:' line")

    def test_mission_order_template(self):
        text = read(TEMPLATES / "mission-order.md")
        self.assertIn(CLOSING_LINE, text)
        last = [ln for ln in text.split("\n") if ln.strip()][-1]
        self.assertEqual(last, CLOSING_LINE)


class SkillTests(unittest.TestCase):
    def test_skill_frontmatter(self):
        data, _ = cr.parse_frontmatter(read(SKILL_MD))
        self.assertEqual(data["name"], "sargento-rea")
        desc = data["description"]
        self.assertLessEqual(len(desc), 1024)
        for trigger in ("sargento", "chief of staff", "chama a tropa"):
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, desc)
        # The checker's grammar cuts a value at " #", and YAML rejects ": "
        # inside a plain scalar, so neither may appear.
        self.assertNotIn(" #", desc)
        self.assertNotIn(": ", desc)

    def test_skill_is_short(self):
        lines = read(SKILL_MD).rstrip("\n").split("\n")
        self.assertLessEqual(len(lines), 150)

    def test_skill_preflight_rules(self):
        text = read(SKILL_MD)
        for needle in (
            "~/.claude/sargento.local.md",
            "<project>/.claude/sargento.local.md",
            "git ls-files --error-unmatch .claude/sargento.local.md",
            "Reply in the user's language; files in this repo stay English.",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)


class SafetyTests(unittest.TestCase):
    def test_package_has_no_suspicious_content(self):
        files = sorted({f for pattern in cr.SCAN_GLOBS for f in ROOT.glob(pattern) if f.is_file()})
        self.assertTrue(files)
        findings = [f for file in files
                    for f in cr.scan_suspicious(file.relative_to(ROOT).as_posix(), read(file))]
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
