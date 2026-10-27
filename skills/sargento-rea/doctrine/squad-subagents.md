# Squad engine: subagents

The fallback when `HERDR_ENV` is not `1`. Each recruit is a Claude Code general-purpose subagent started with the Agent tool. If the overlay says to stop outside herdr, stop instead and tell the user how to open herdr.

## Dispatch

- One general-purpose subagent per recruit. Dispatch the whole wave in one message, so the recruits run in parallel.
- The prompt is the full mission order, built from [templates/mission-order.md](../templates/mission-order.md). A subagent sees none of your conversation either. In a study, save the order to `orders/<name>.md` first, then send its text.
- Build recruits get worktree isolation (`isolation: "worktree"`), so each works in its own worktree and branch. Research recruits work in the study folder without one.
- The squad-size limits in [SKILL.md](../SKILL.md) apply here too.

## Reports

- A subagent's answer comes back to you as text. Save each one to `reports/<name>.md` yourself, or, if the order told the recruit to write that file, check that it exists.
- Wait until every recruit in the wave has answered before you consolidate. Never write a recruit's result before it arrives.
- To follow up with a recruit, continue that same subagent if the harness allows it (SendMessage). Otherwise dispatch a new one whose order includes the earlier report.

## Review and cleanup

- Review a build recruit's work as in the Build mission: read the diff with `git -C`, run the tests from outside its worktree, then merge.
- When a subagent changed files, the harness keeps its worktree and returns the path and branch with the result. Remove both after the merge with `git -C "<repo>" worktree remove "<path>"` and `git -C "<repo>" branch -d "<branch>"`.

## What is lost compared to herdr

- **No live view.** You see a recruit's work only when it answers.
- **No answering approval prompts.** Recruits run under the session's permissions, and you cannot approve a command for them. Each order therefore says: if a command is refused, stop and report it instead of working around it.
