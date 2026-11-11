# Agenda rules

The agenda is `.project-crew/agenda.json` at the repo root. It is the only record of the loop. A
new session that reads it must be able to continue with no other context.

## Who writes

Only the main session writes the agenda. A background worker reads it and never writes it. A
worker reports in `.project-crew/reports/<task id>.md`, and the main session copies what matters
into the agenda on its next pass.

## How to write

1. Read the file from disk first. Do not write from memory of an earlier read.
2. Make all changes of one step in one write.
3. Take every timestamp from `date -u +%Y-%m-%dT%H:%M:%SZ`, run in the same step. Never type a
   time by hand.
4. Set `updatedAt` on the file and on each task you changed.
5. Check the result: `jq empty .project-crew/agenda.json` must exit 0. Without jq, use
   `python3 -m json.tool .project-crew/agenda.json >/dev/null`.

## Top-level fields

| Field | Meaning |
|---|---|
| `version` | schema version, `1` |
| `updatedAt` | time of the last write |
| `budget` | `low`, `medium` or `high`. Only the budget command changes it. |
| `repo.defaultBranch` | the branch PRs target |
| `repo.testCommand` | the repo's own test command, asked once at setup. `none` if the repo has no tests. |
| `repo.tracker` | `github` when gh works in this repo, else `text` |
| `workerPermissionMode` | permission mode for background workers, asked once when the budget first leaves low. `null` until then. |
| `cadence.mode` | `manual` (low) or `cron` (medium, high) |
| `cadence.intervalMinutes` | `null`, `60` or `30` |
| `cadence.cronId` | id that CronCreate returned, or `null` |
| `cadence.cronCreatedAt` | when that cron was made. Recurring crons expire after 7 days. |
| `cadence.lastPassAt` | when the last status pass ended |
| `tasks` | list of tasks, oldest first |
| `pendingUserActions` | open asks for the human |

## A task

```json
{
  "id": "t1",
  "title": "Login form accepts an empty password",
  "issue": 42,
  "state": "queued",
  "confidence": null,
  "worktree": null,
  "branch": null,
  "pr": null,
  "worker": null,
  "notes": "",
  "updatedAt": "2026-01-01T00:00:00Z"
}
```

- `id`: `t` plus the next free number. Never reuse an id.
- `title`: one line. For a GitHub issue, the issue title.
- `issue`: the issue number, or `null` for a plain text task.
- `confidence`: `null` before the gate, then `HIGH`, `MEDIUM` or `LOW`.
- `worktree`: path relative to the repo root, `.project-crew/worktrees/<id>`.
- `branch`: `crew/<id>-<short-slug>`.
- `pr`: the PR URL, or `null`.
- `worker`: id of the background session that carries the task now, or `null`.
- `notes`: a few lines at most. The human's words for the task, the root cause as `file:line`,
  the answer to an ask, why a task was dropped. Long findings stay in the report file or the PR.

Done and dropped tasks stay in the list until the clean command archives the agenda.

## States

| State | Meaning | Leaves when |
|---|---|---|
| `queued` | waiting for a free slot | a slot opens: `investigating` |
| `investigating` | reproducing and finding the cause, no code change yet | the gate is judged: `building` on HIGH, else `gated` |
| `gated` | stopped, an ask is open for the human | the human answers: back to `investigating`, on to `building`, or `dropped` |
| `building` | failing test first, then the change, in the task worktree | the test command passes: `reviewing` |
| `reviewing` | the diff is under review at the budget's depth | review is clean and the commit is made: `drafted` |
| `drafted` | a draft PR is open, or the branch is ready where there is no gh | the human merges: `done`. The human closes it: `dropped`. The human asks for changes: `building`. |
| `done` | merged by the human | never |
| `dropped` | stopped on the human's word, or the PR was closed unmerged | never |

A task moves one step at a time and only forward, except the three returns the table names.

## An ask

```json
{
  "task": "t1",
  "ask": "Cannot reproduce on main. Which browser and which account type showed it?",
  "askedAt": "2026-01-01T00:00:00Z",
  "satisfiedWhen": "the human names a browser and account type, or drops t1"
}
```

- One ask per decision. Say what you found, what you recommend, and the one thing you need.
- `satisfiedWhen` is something you can observe: an answer in the session, a merged PR, a renewed
  login.
- Remove an ask in the same write that acts on its answer. Quote the answer in the task `notes`.
- `task` is `null` for an ask about the loop itself, such as an expired gh login.
