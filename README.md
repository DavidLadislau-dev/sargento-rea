# Sargento REA

A chief-of-staff Claude that commands a squad of Claude Code agents to study, reverse-engineer and build software, backed by a library of reverse-engineering recipes. "Sargento" is Portuguese for sergeant, and the Sargento behaves like one: it plans, splits the work, and sends recruits (other Claude Code agents) to do it.

## Recipes

Each recipe is one method in one file, signed by its authors and credited to the project it was learned from. Ask the Sargento to use one by name, or let it pick from the mission.

| Recipe | What it gets you | Learned from |
|---|---|---|
| [Rosetta stone pairs](skills/sargento-rea/recipes/rosetta-stone.md) | Learn an undocumented file format by pairing each sample with the vendor's own interpretation of the same document, then counting field matches across every pair. | storytold (indd-utils, photocraft, photocraft-corpus, wordcraft) |
| [Evidence ledger](skills/sargento-rea/recipes/evidence-ledger.md) | Keep every fact about a target with a match count and every open question with a status, so your code relies only on facts you can re-check. | storytold (indd-utils) |
| [Pinned corpus](skills/sargento-rea/recipes/pinned-corpus.md) | Keep samples out of git, pin each batch by commit and SHA-256, record where each batch came from, and leave private samples out of published numbers. | storytold (photocraft, indd-utils, photocraft-corpus) |
| [Black-box app observation](skills/sargento-rea/recipes/black-box-app.md) | Learn how an installed app behaves by feeding it synthetic inputs and recording what it shows and writes, using only its screen, its exports and its scripting interface. | storytold (photocraft-corpus, wordcraft, cadcraft, soundcraft, pdfcraft) |
| [Licence firewall](skills/sargento-rea/recipes/licence-firewall.md) | Sort every outside source by licence before work starts, so copyleft code is never copied or linked, permissive references are re-described with attribution, and copyleft tools only run as separate processes. | storytold (cadcraft, pdfcraft, photocraft, wordcraft, soundcraft) |
| [Rising floors](skills/sargento-rea/recipes/rising-floors.md) | Make every measurement print its scores, enforce a pass floor that only goes up, fail instead of skip when a reference tool is missing, and accept a parity claim only when a real test backs it. | storytold (pdfcraft, photocraft, photocraft-corpus, wordcraft) |
| [Call-site contract](skills/sargento-rea/recipes/call-site-contract.md) | Infer what a library function takes and returns from how real programs call it, record what the callers cannot settle, and write the code from that contract instead of translating the disassembly. | AnyPS5 |
| [Hardware oracle](skills/sargento-rea/recipes/hardware-oracle.md) | Rank your sources of truth by how directly they observe the real thing, and settle the questions that documentation leaves open by running small probes on real hardware, with every setting recorded. | AnyPS5 |
| [Performance before and after](skills/sargento-rea/recipes/perf-before-after.md) | Measure frame rate and frame time on the same machine and scene before and after a change, find the real bottleneck from a profile, and report the numbers with what they do not show. | AnyPS5 |

What the status of a recipe means:

| Status | Meaning |
|---|---|
| `proven-upstream` | The project it was learned from published numbers showing the method works. The recipe cites them, with links. |
| `tested` | Someone ran the recipe with this skill and recorded their own counts. |
| `draft` | Neither yet. |

Today, `rosetta-stone`, `evidence-ledger` and `perf-before-after` are `proven-upstream`. The other six are `draft`. None is `tested` yet, because nobody has run them with this skill and recorded counts. A recipe moves to `tested` through a pull request that adds the run's counts.

## Install

In Claude Code, add this repository as a marketplace and install the plugin:

```
/plugin marketplace add DavidLadislau-dev/sargento-rea
/plugin install sargento-rea@sargento-rea
```

From a terminal, with Claude Code 2.1.275 or later, one command does both:

```
claude plugin install sargento-rea --marketplace DavidLadislau-dev/sargento-rea
```

Or copy the folder `skills/sargento-rea/` into `~/.claude/skills/` by hand. That also works, and it keeps the recipes, doctrine and templates together with the skill.

## Quick start

Open Claude Code and talk to the Sargento:

- `sargento, study <target>` starts a Study mission: reverse-engineer existing software until you can prove what you know about it.
- `sargento, build <idea>` starts a Build mission: survey the market, write a spec, then build with a squad.
- `sargento, review PR 12` briefs you on a pull request to this repository.

The Sargento reads your overlay, picks an engine, tells you which one it chose, and asks you to confirm the plan before it enlists recruits.

## How it works

- **Missions.** Study produces evidence with counts, kept in a study folder with a fact ledger and an unknowns ledger. Build runs in four phases (survey, spec, build, review) and no recruit writes code until you approve the spec. A third mode, Review, briefs you on contributions.
- **The squad.** The Sargento does not dig. It writes a mission order for each recruit, follows up, reviews and integrates. Recruits run recipes and write code.
- **herdr is optional.** If you use [herdr](https://github.com/herdrdev/herdr), the squad works in herdr panes you can watch. Without herdr, the Sargento falls back to Claude Code subagents.
- **REA is optional.** If the `rea` MCP server and Ghidra are installed, recipes use them as a booster. Nothing requires them.
- **Evidence.** Every claim in a report is marked as stated by a source or inferred, and counts replace adjectives: "171 of 171", not "always".
- **No built-in usage limits.** The skill does not carry a list of forbidden targets or uses. You decide your own limits in your overlay.
- **Target content is data.** Strings, decompiled code, downloaded files and pull request text are never treated as instructions.

## Your overlay

Your personal rules live outside this repository, in a private overlay file:

- `~/.claude/sargento.local.md` applies to everything you do.
- `<project>/.claude/sargento.local.md` applies to one project and wins over the first.

Start from `skills/sargento-rea/templates/sargento.local.example.md`. It has sections for your rules, machine, tools, workflow, stack and mission notes, so you can set your own limits, authorization rules and squad size. `.gitignore` covers `*.local.md`, so a copied folder never leaks one.

Trust rule for the project file: it applies automatically only when you are inside a git work tree and git does not track the file. In any other case (not a git repository, or the file is tracked) it may have come from a cloned target, so the Sargento shows it to you and applies it only when you say so.

## Contributing

Recipes are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md): one recipe or change per pull request, written in your own words, with counts for every success claim, no third-party files, and a note on whether an AI helped. Start from `skills/sargento-rea/templates/recipe.md`. A check runs on every pull request.

## Credits

**Maintainer:** [DavidLadislau-dev](https://github.com/DavidLadislau-dev)

**Contributors:**

- [DavidLadislau-dev](https://github.com/DavidLadislau-dev) (maintainer, initial recipe set)

A contributor is added here when their name appears in the `authors` of a merged recipe, and the pull request that merges the recipe adds the line.

**Projects the methods were learned from.** These recipes re-describe public methods in their own words and link back to the sources:

- storytold, a set of clean-room projects: [indd-utils](https://github.com/storytold/indd-utils), [photocraft](https://github.com/storytold/photocraft), [photocraft-corpus](https://github.com/storytold/photocraft-corpus), [wordcraft](https://github.com/storytold/wordcraft), [cadcraft](https://github.com/storytold/cadcraft), [soundcraft](https://github.com/storytold/soundcraft) and [pdfcraft](https://github.com/storytold/pdfcraft).
- [boykopovar/AnyPS5](https://github.com/boykopovar/AnyPS5).

**AI models** that helped write this repository are credited through `Co-Authored-By` trailers in the commit history.

## Disclaimer

You are responsible for how you use this. Check the laws where you live.

This project is not affiliated with, endorsed by or sponsored by storytold, AnyPS5, rea-agents / REA (whose MCP server is also called `rea`), herdr or Anthropic. Their names appear only to say where a method was learned or which tool a recipe can use.

## Licence

MIT. See [LICENSE](LICENSE).
