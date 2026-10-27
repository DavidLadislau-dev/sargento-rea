# My Sargento overlay

Copy this file to `~/.claude/sargento.local.md` to apply it everywhere, or to `<project>/.claude/sargento.local.md` for one project; the project file wins. Your rules here override the skill's defaults.

Keep the file out of git: add `*.local.md` to the project's `.gitignore`. The Sargento applies a project overlay that git tracks only after you confirm it.

Replace each example line with your own, or delete the section.

## About me

> Example: Reply in Spanish. Keep reports short and skip the pleasantries.

## My rules

> Example: Before testing a system I don't own, ask whether written authorization exists; without it, do not start.

## My machine

> Example: Max build recruits: 2. Stop the container engine before a heavy build.

## My tools

> Example: Stop outside herdr instead of using subagents: no. REA and Ghidra are installed.

## My workflow

> Example: After each finished subtask, run `my-log add "<project>" "<what was done>"`.

## My stack

> Example: Python 3.12 with FastAPI, PostgreSQL and a React front end.

## Missions

> Example: Mission notes live in `~/notes/missions/`, one file per mission, each with a "resume here" line.
