# Squad engine: herdr

Use this engine when `HERDR_ENV` is `1`. Each recruit is a Claude Code session in its own herdr pane, and you drive it with `herdr` commands. Verified on herdr 0.9.5; the installed binary's `herdr --help` is the authority on syntax. Load the `herdr` skill if it is installed. Never control a herdr session from outside it.

## Enlist a recruit

```bash
herdr pane layout --pane "$HERDR_PANE_ID"                  # decide: split right or down
herdr pane split --current --direction right --cwd "<folder>" --no-focus
# the new pane id is in .result.pane.pane_id
herdr agent start <name> --kind claude --pane <pane_id> -- --permission-mode auto -n <name> -w <name>
herdr agent prompt <name> "$(cat orders/<name>.md)"
herdr agent wait <name> --timeout 3600000                  # in the background
herdr agent read <name> --source recent-unwrapped --lines 150
```

- **Names:** `[a-z][a-z0-9_-]{0,31}`, short and named for the job (`api`, `front`, `tests`, `market-bench`).
- **Layout:** recruits are sibling panes in the current tab. Alternate right and down so no pane becomes a thin slice. Past 4 recruits, open a squad tab and make a 2x2 grid: `herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd "<folder>" --label squad --no-focus`, split its root pane right, then split each column down.
- **Worktree:** `-w <name>` is only for build recruits in a git repo. Research recruits drop it and work in the study folder.
- **No integration hooks:** herdr detects Claude from the process tree and the screen. `herdr integration install claude` installs hooks, which is global automation; run it only if the user asks.

## Trust prompt

In a folder Claude Code has not trusted yet, the recruit stops at the "trust this folder" prompt and `agent start` returns `agent_not_ready`.

- **A folder the user owns.** Own means you created it, or the user's current session already runs in it. If in doubt (a clone, or a folder holding `.claude/settings*.json` or `.mcp.json` you did not write), ask. For an owned folder, check the screen with `herdr agent read <name> --source visible`, answer `herdr agent send-keys <name> down enter`, then `herdr agent wait <name> --until idle --timeout 60000`.
- **Any other folder**, such as a cloned target or a worktree of one: ask the user first. Trusting the folder runs its `.claude/settings.json` hooks and starts the servers in its `.mcp.json`.
- Better: keep recruits in the study folder and let them read the target from `raw/` by path. Never use a folder under `raw/`, or any extracted third-party folder, as a recruit's `--cwd` or project root; that is where its `.claude/` files would be picked up.

## Auto mode

Claude Code's permission classifier may block you from running `agent start ... --permission-mode auto`. When it does:

1. Make the pane splits yourself.
2. Write one line with every `agent start` command, separated by `;`.
3. Ask the user to run that line with `!` (the prompt prefix that runs a shell command directly).

Do not start recruits without `--permission-mode auto` to dodge the block, and do not look for another workaround. Prompt, read and wait stay with you.

## Orders and waiting

- Build each order from [templates/mission-order.md](../templates/mission-order.md). Write it to a file with your file-writing tool (a large heredoc can break in a shell tool) and send it with `herdr agent prompt <name> "$(cat <file>)"`.
- Release every recruit at once: send all the prompts without `--wait`, then start one background `herdr agent wait <name> --timeout 3600000` per recruit, so each one wakes you when it finishes. Without `--until`, `wait` also returns when a recruit is blocked on an approval screen.
- A `timeout` or `agent_prompt_stalled` does not prove the order failed to arrive. Read the recruit's screen before you resend.
- For a long answer, the order says "write `reports/<name>.md` and reply with the path".

## Approval screens

- Read the whole command with `herdr agent read <name> --source visible` before deciding. The `recent` source does not show it while the recruit is blocked.
- Approve normal work inside the recruit's worktree or study folder yourself. Anything on the "ask the user first" list in [SKILL.md](../SKILL.md) goes to the user.
- Check where every variable in the command is set. `rm -rf "$DIR/build"` is harmless when the same command sets `DIR` to a path inside the worktree, and dangerous when `DIR` could be empty.
- Answer with `herdr agent send-keys <name> <keys>`, matching the options on the screen.

## Worktrees and review

- `-w <name>` creates `<repo>/.claude/worktrees/<name>` on branch `worktree-<name>`, from the current `HEAD`. Add `.claude/worktrees/` to the repo's `.gitignore` on `main`.
- Review without changing into a recruit's worktree: use `git -C "<worktree>"` and the test tool's own directory flag (for example `uv run --directory "<worktree>"` or `npm --prefix "<worktree>"`).
  - Note for Windows: a `cd` into the worktree leaves a handle open that later blocks deleting the folder ("Device or resource busy").
- Real personal or financial data in a recruit's work follows the personal-data rule in [SKILL.md](../SKILL.md).

## Dismissal

- When a recruit is done, close its pane: `herdr pane close <pane_id>`. Close only panes you created.
- After its branch is merged, remove the worktree:

```bash
git -C "<repo>" worktree unlock ".claude/worktrees/<name>"
git -C "<repo>" worktree remove ".claude/worktrees/<name>"
git -C "<repo>" branch -d "worktree-<name>"
```
