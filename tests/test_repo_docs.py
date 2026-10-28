import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

README_HEADINGS = [
    "## Recipes",
    "## Install",
    "## Quick start",
    "## How it works",
    "## Your overlay",
    "## Contributing",
    "## Credits",
    "## Disclaimer",
    "## Licence",
]


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def section(text, heading):
    start = text.index(heading)
    nxt = re.search(r"^## ", text[start + len(heading):], re.M)
    end = start + len(heading) + nxt.start() if nxt else len(text)
    return text[start:end]


class ReadmeTests(unittest.TestCase):
    def test_readme_sections_in_order(self):
        text = read("README.md")
        positions = []
        for heading in README_HEADINGS:
            matches = [m.start() for m in re.finditer("^" + re.escape(heading) + r"\s*$", text, re.M)]
            self.assertEqual(len(matches), 1, heading)
            positions.append(matches[0])
        self.assertEqual(positions, sorted(positions))

    def test_readme_disclaimer_and_install(self):
        text = read("README.md")
        self.assertIn("You are responsible for how you use this. Check the laws where you live.", text)
        self.assertIn("/plugin marketplace add DavidLadislau-dev/sargento-rea", text)
        self.assertIn("/plugin install sargento-rea@sargento-rea", text)
        disclaimer = section(text, "## Disclaimer")
        for name in ("storytold", "AnyPS5", "rea-agents", "herdr", "Anthropic"):
            self.assertIn(name, disclaimer)

    def test_readme_explains_name(self):
        self.assertIn("Portuguese for sergeant", read("README.md"))


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.text = read(".github/workflows/check-recipes.yml")

    def test_workflow_hardening(self):
        text = self.text
        self.assertIn("pull_request:", text)
        self.assertIn("push:", text)
        self.assertNotIn("pull_request_target", text)
        self.assertRegex(text, r"permissions:\s*\n\s+contents: read")
        uses = re.findall(r"^\s*-?\s*uses:\s*(\S+)", text, re.M)
        self.assertTrue(uses)
        for ref in uses:
            self.assertRegex(ref, r"@[0-9a-f]{40}$")
        self.assertNotIn("secrets.", text)

    def test_workflow_runs_checker_and_tests(self):
        self.assertIn("python3 scripts/check_recipes.py", self.text)
        self.assertIn("python3 -m unittest discover -s tests -v", self.text)
        self.assertIn("ubuntu-latest", self.text)


class TemplateTests(unittest.TestCase):
    def test_pr_template_fields(self):
        text = read(".github/pull_request_template.md")
        for heading in (
            "## What this adds or changes",
            "## Where the method comes from",
            "## How you proved it",
            "## AI assistance",
        ):
            self.assertIn(heading, text)
        self.assertEqual(len(re.findall(r"^- \[ \] ", text, re.M)), 4)
        for phrase in ("template sections", "own words", "third-party files", "downloads and runs code"):
            self.assertIn(phrase, text)

    def test_issue_forms(self):
        for name in ("new-recipe.yml", "recipe-problem.yml"):
            text = read(".github/ISSUE_TEMPLATE/" + name)
            for key in ("name:", "description:", "body:", "validations:", "required: true"):
                self.assertIn(key, text, name)


class ContributingTests(unittest.TestCase):
    def test_contributing_covers_rules(self):
        text = read("CONTRIBUTING.md")
        for phrase in (
            "skills/sargento-rea/templates/recipe.md",
            "python scripts/check_recipes.py",
            "python -m unittest discover -s tests -v",
            "proven-upstream",
            "tested",
            "draft",
            "SHA-256",
            "written by hand",
            "volunteer",
        ):
            self.assertIn(phrase, text)


class PrivacyTests(unittest.TestCase):
    def test_no_local_paths_or_emails(self):
        for rel in ("README.md", "CONTRIBUTING.md"):
            text = read(rel)
            self.assertNotRegex(text, r"[A-Za-z]:[\/]+Users", rel)
            self.assertNotRegex(text, r"[\w.+-]+@(gmail|hotmail|outlook)\.", rel)
            self.assertNotIn("<!--", text, rel)


if __name__ == "__main__":
    unittest.main()
