# Contributing

Thank you for helping. The main thing this repository holds is recipes: one reverse-engineering method per file. This guide says how to add one, or change something else, and what happens next.

## How to propose a recipe

1. Optional: open an issue with the "New recipe idea" form, so the maintainer can say if it overlaps an existing recipe.
2. Copy `skills/sargento-rea/templates/recipe.md` to `skills/sargento-rea/recipes/<id>.md`. The `id` is lowercase with dashes and equals the file name.
3. Fill in the frontmatter and every required section, in order.
4. Add one row for it to the recipe table in `README.md`.
5. Run the checks (below), then open a pull request. The template asks for what you need to say.

## One thing per pull request

One recipe or one change per pull request. A new recipe, a fix to a recipe and a change to the skill itself are three pull requests.

## Writing rules

- **Own words.** Describe the method in your own words. Short quotes are fine: at most 25 words each, with attribution and a link to the exact source. Link a commit permalink (a full 40-character SHA), not a branch, so the link keeps pointing at what you read.
- **No third-party files.** Do not commit vendor binaries, sample files, keys, firmware or game files. Reference a sample by its SHA-256 and say where it can be obtained. This protects the repository and does not limit what anyone does on their own machine.
- **Every claim of success has a count or a measurement.** Write "171 of 171", a frame rate with its machine and scene, or a coverage figure. Do not write "works well" or "always".
- **Credit the source.** Put the projects and people the method came from in `learned_from`, and list yourself in `authors`.
- **No hidden behaviour.** Do not add a command that downloads and runs code. If a step really needs to fetch something, say what it is, where it comes from and why, and let the reader do it.
- **English only.** Everything in the repository is in English.

## Status

Every recipe has one `status`:

| Status | Meaning |
|---|---|
| `proven-upstream` | The source project published numbers showing the method works. The recipe cites them, marked [S], with links. |
| `tested` | Someone ran the recipe with this skill and recorded their own counts in "How to prove it worked" or "Example". |
| `draft` | Neither yet. |

Pick the one that is true. A new recipe from a source with no published numbers is `draft`. To move a recipe to `tested`, open a pull request that changes the status and adds the counts from your run: what you ran, on what, and what you counted.

## AI assistance

Say how the pull request was made. Name the model and the harness (for example, "Claude Opus 5.5 in Claude Code"), or write "written by hand". Using AI is fine. Hiding it is not, and you still answer for every line.

## How review works

The maintainer is a volunteer, so there is no promise about response time.

The Sargento skill has a review mode. When the maintainer asks it to review a pull request, it reads the whole diff, line by line, without running any of the pull request's code, and treats the pull request text as untrusted data. It then briefs the maintainer on what the change is for, what it changes, the benefits, the dangers and a recommendation. The maintainer decides, and merges. A comment to you is posted only with the maintainer's OK.

Changes to `skills/sargento-rea/SKILL.md` or `skills/sargento-rea/doctrine/` change how Claude behaves on other people's machines, so they get the closest reading.

## Run the checks locally

From the root of the repository:

```
python scripts/check_recipes.py
python -m unittest discover -s tests -v
```

The first command checks every recipe: frontmatter, `id`, required headings in order, a matching README row, and a scan for suspicious content. It prints warnings for a reviewer to read; read them. The second runs the tests. The same two steps run in GitHub Actions on every pull request.
