# Build mission

Survey the market, write a spec and build a new app with a squad, in four phases. No recruit writes code before the user approves the spec.

## 1. Survey

Run the briefing with the user, then send research recruits out in parallel.

- **Briefing:** the problem, the current process, who uses it, and what success looks like.
- **Market benchmark:** existing products, their features, price, reviews, and what their users complain about.
- **Existing systems:** check whether something the user already runs solves part of the problem before building from scratch. The overlay may point to an inventory.
- **Constraints:** technical and legal ones (privacy law, regulated APIs, app store rules).
- **Stack:** propose one aligned with the user's usual stack, from the overlay's My stack section.

3 to 5 research recruits, one topic each, each writing `survey/<topic>.md` in the mission folder (the new project's repo, or the folder the overlay names). You consolidate them into `survey/consolidated.md` and brief the user.

## 2. Spec and plan

- If the superpowers plugin is installed, run its `brainstorming` skill, then `writing-plans`.
- Otherwise write an equivalent spec yourself: the problem and users, scope and non-goals, architecture, data, and the definition of done. Then a plan that splits the work into independent fronts, each with its interfaces, files and tests.
- Either way, the user approves the spec before any recruit writes code.

## 3. Parallel offensive

- One recruit per independent front, each in its own worktree and branch. Fronts that depend on each other run one after the other.
- At most 2 build recruits at a time, and check free RAM before a heavy build, unless the overlay sets other limits.
- Each order, from [templates/mission-order.md](../templates/mission-order.md), carries the front's task from the plan, the interfaces it must respect, and its definition of done as tests to pass.

## 4. Review and integration

- Read each recruit's whole diff from outside its worktree: `git -C "<repo>" diff main...<branch>`. Under herdr the branch is `worktree-<name>`.
- Run the tests yourself, pointing the test tool at the worktree instead of changing into it.
- Merge into `main`, then show the user the result working: run it, open the screen, call the endpoint.
- Commit as the overlay says. Pushing is publishing: push only when the overlay says so or the user agrees.
- Dismiss recruits and remove their worktrees as the engine doctrine says.
