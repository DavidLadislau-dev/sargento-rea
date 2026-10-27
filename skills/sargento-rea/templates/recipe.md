---
id: your-recipe-id          # same as the file name, lowercase with dashes
title: Short name of the method
summary: One sentence on what the method gets you.
mission: study              # study | build
needs: [what the user must have, another input]
tools: [a tool the steps use, optional rea]
authors: [your-github-handle]
learned_from:
  - name: project or person the method comes from
    url: https://github.com/owner/repo
status: draft               # proven-upstream | tested | draft
---

# Short name of the method

Copy this file to `skills/sargento-rea/recipes/<id>.md`, add a row for it to the README recipe table, and replace every prompt line below with your own words. Run `python scripts/check_recipes.py` before you open the pull request.

Pick `status` from this table:

| Status | Meaning |
|---|---|
| `proven-upstream` | The source project published numbers showing the method works. The recipe cites them, marked [S], with links. |
| `tested` | Someone ran the recipe with this skill and recorded their own counts in "How to prove it worked" or "Example". |
| `draft` | Neither yet. |

## When to use

The situation, and the question this method answers better than the other recipes.

## What you need

Inputs, tools and access, with the optional ones marked as optional.

## Steps

Numbered steps a recruit can follow without asking anything.

## How the Sargento splits the work

Which recruits to enlist, what each one's mission order says, and what each one hands back.

## How to prove it worked

What to count, and what the numbers look like when the method works.

## Sources and credits

Every source with a link, and short attributed quotes only. Mark claims [S] stated by a source or [I] inferred.

## Notes

Optional. Constraints worth knowing, for example "needs the vendor app installed", or rules the source project set for itself.

## Example

Optional. One real run, with its counts.
