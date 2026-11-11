# project-crew

A chief of staff for one software project, as a Claude Code plugin.

You keep one Claude Code session open in your repo and talk only to it. The session keeps a JSON
agenda of tasks and carries each task end to end:

1. It investigates the task and tries to reproduce it.
2. It gates on confidence. It builds only when the evidence is HIGH. Otherwise it asks you.
3. It builds in a git worktree, failing test first.
4. It reviews its own diff and strips the filler.
5. It makes one squashed commit and opens a draft GitHub PR.

You read the PR, mark it ready and merge it. The plugin never marks a PR ready, never merges, and
never pushes to your default branch.

## Install

```
/plugin marketplace add wannaFlyKa/project-crew
/plugin install project-crew@project-crew
```

Requirements:

- Claude Code and git.
- The `gh` CLI, logged in, for issues and draft PRs. Without it, tasks are plain text and each
  one stops at a ready branch for you to open the PR.
- For the medium and high budgets, a Claude Code version with background sessions
  (`claude --bg`) and the bundled `/code-review` skill.

## Commands

Run these inside the repo, in the session you want to be the chief.

| Command | What it does |
|---|---|
| `/project-crew:chief` | Set up the loop in this repo, or resume it in a new session |
| `/project-crew:chief add <task>` | Queue a task: free text, `#12`, or an issue URL |
| `/project-crew:chief status` | One pass over the agenda, by hand |
| `/project-crew:chief budget low\|medium\|high` | Write the budget to the agenda |
| `/project-crew:chief clean` | End a finished loop and archive the agenda |
| `/project-crew:rmslop` | Strip AI filler from the pending diff |
| `/project-crew:ste100 <text or path>` | Write or review text in Simplified Technical English |

After setup you can also use plain words in the chief session: "add ...", "status", "drop t3",
or the answer to a question it asked.

Setup asks one question: the command that runs your tests. A task is done when that command
passes, rmslop has run, the change is one squashed commit, and a draft PR is open.

## Budget

The budget decides how much runs without you. It starts at low and changes only when you run
the budget command. It never picks a model: your `/model` choice applies to the chief and to
every worker.

| Budget | Status pass | Who does the work | Review | Rough guide to spend |
|---|---|---|---|---|
| `low` (default) | only when you ask | the chief session, one task at a time | one self-check of the diff | Lowest. Nothing runs while you are away. You pay for the work on each task and for nothing else. |
| `medium` | cron, every 60 minutes | 1 background worker in its own worktree | `/code-review medium` | More. About 24 passes a day while the session is open, each one a small read even when nothing changed. Each task also costs a full worker session and a medium review. |
| `high` | cron, every 30 minutes | up to 3 background workers | `/code-review high --fix` | Most. About 48 passes a day, up to 3 worker sessions at once, and the deepest of the three reviews on every task. |

This is a rough guide, not a measurement. Real spend depends on your model, your repo and the
size of each task. Start at low and move up when waiting on the chief costs you more than tokens.

A cron fires only while the chief session is open and idle. It expires after 7 days, and
`/project-crew:chief` in a new session makes a fresh one.

## The confidence gate

The chief builds only when all five hold, each with evidence:

1. The problem is reproduced.
2. The root cause is named at `file:line`.
3. Other hypotheses are ruled out.
4. The blast radius is named.
5. A failing test can be written.

If one is missing, the task stops in the `gated` state and the chief shows you one line that
starts with "Needs you:". Your answer moves the task on.

## What it writes in your repo

Everything lives in `.project-crew/` at the repo root. Setup adds that folder to
`.git/info/exclude`, so no tracked file changes.

| Path | Holds |
|---|---|
| `.project-crew/agenda.json` | budget, tasks, open questions, cadence. Only the chief session writes it. |
| `.project-crew/worktrees/<task id>/` | one git worktree for each task, on branch `crew/<task id>-<slug>` |
| `.project-crew/reports/` | worker briefs, worker reports and PR bodies |

Task states: `queued`, `investigating`, `gated`, `building`, `reviewing`, `drafted`, `done`,
`dropped`.

The agenda is the whole memory of the loop. When a session gets long, open a new one in the repo
and run `/project-crew:chief`.

## Skills

| Skill | Purpose |
|---|---|
| `chief` | the loop described above |
| `rmslop` | cuts comments that repeat the code, narration of the change, needless guards and vague commit messages from a diff |
| `ste100` | writes text to the rules of ASD-STE100 Simplified Technical English and checks it with `scripts/ste_check.py`, a linter that needs only the Python standard library |

ASD-STE100 is a trademark of ASD. The `ste100` skill is unofficial and does not include the ASD
dictionary.

## License

MIT. See [LICENSE](LICENSE).
