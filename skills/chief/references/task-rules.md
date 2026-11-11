# Task rules

How one task goes from a request to a draft PR. Whoever carries the task follows this file: the
main session on the low budget, a background worker on medium and high.

## What you are given

- the task: id, title, issue number if any, the human's own words
- the worktree path and the branch
- the base: `origin/<defaultBranch>` when the repo has an `origin` remote, else `<defaultBranch>`
- the test command, the budget, the tracker (`github` or `text`)

Work only inside the task worktree, by path (`cd <worktree>` or `git -C <worktree>`). Never change
a file in the main checkout.

## If you are a worker

- Never write `.project-crew/agenda.json`. Your voice is `.project-crew/reports/<task id>.md`.
- Keep the first line of the report as `state: <state>` and update it each time the state changes.
- Never ask the human a question. Nobody watches a background session, so a question there waits
  forever. Write the question in the report, set `state: gated`, and end.
- Never start another worker or a cron. Never pass or change a model.
- End your turn when the task is `gated` or `drafted`. The main session reads the report.

## 1. Worktree

The main session makes it before the task starts:

```bash
git -C "$root" fetch origin
git -C "$root" worktree add -b "crew/<id>-<slug>" ".project-crew/worktrees/<id>" "<base>"
```

Skip the fetch when the repo has no `origin` remote. One task per worktree. A task that returns
from `gated` or `drafted` reuses its worktree and branch.

## 2. Investigate (state `investigating`)

Change no tracked file in this step. `git status --porcelain` must be empty when you reach the
gate.

1. Read the task. For an issue: `gh issue view <n> --comments`.
2. Reproduce it. Run the code or write a throwaway check outside the tree. Reading code and
   deciding it "must" fail is not a reproduction.
3. Find the cause and name it as `file:line` with the mechanism in one or two sentences.
4. List the other explanations you considered, and the observation that rules each one out.
5. Name the blast radius: every file and behavior the change will touch, and who calls them.
6. Describe the test you will write first, and why it fails today.

## 3. Confidence gate

HIGH needs all five. Each one needs evidence you can paste, not a belief.

| # | Criterion | Evidence |
|---|---|---|
| 1 | Reproduced | the command you ran and the wrong output it gave |
| 2 | Root cause at `file:line` | the line, and how it produces that output |
| 3 | Other hypotheses ruled out | each one with the fact that kills it |
| 4 | Blast radius named | the list of files and behaviors the fix touches |
| 5 | A failing test can be written | the test name, its assertion, and why it is red now |

For a feature or a refactor, read the criteria this way: (1) you showed the current behavior and
the gap, (2) you named the place of the change at `file:line`, (3) you ruled out the other
designs with a reason each, (4) and (5) as written.

Call it MEDIUM when you have a recommendation but one or more criteria lack evidence. Call it LOW
when you cannot reproduce it or cannot name a cause.

- HIGH: go to step 4.
- MEDIUM or LOW: do not build. Record the confidence, what you found, what you recommend, and the
  one question that would settle it. Set the state to `gated`. The main session turns the question
  into a `pendingUserActions` entry. Stop work on this task.

The human can answer a gated task with new facts, which sends it back to step 2, or with a plain
go-ahead. A go-ahead is the human's decision: keep the measured confidence, quote the go-ahead in
the notes, and go to step 4.

## 4. Build (state `building`)

1. Write the failing test first. Run it and see it fail for the reason you named at the gate. If
   it passes, or fails for another reason, your root cause is wrong: go back to step 2.
2. Make the smallest change that turns the test green. Follow the style of the code around it.
3. If the change needs a file outside the blast radius you named, stop. The gate no longer holds.
   Return to step 3 with the new facts.
4. Run the full test command from the agenda in the worktree. It must pass. Do not swap in a
   narrower command, and do not skip, delete or loosen a test to get there.
5. If a test fails that your change did not touch, run it on the base. If it fails there too,
   that is a finding for the human: gate the task and say so.

If `testCommand` is `none`, run the new test alone and say in the PR body that the repo has no
test command.

## 5. Review (state `reviewing`)

Review the whole diff against the base: `git diff <base>...HEAD` plus any uncommitted change.

| Budget | Review |
|---|---|
| low | One self-check. Read the diff once from top to bottom and answer: does every hunk serve the task, does anything outside the blast radius change, is an error path or edge case missing, did debug output or a stray file get in. Fix what you find. |
| medium | Run `/code-review medium` on the diff. Fix each confirmed finding yourself. |
| high | Run `/code-review high --fix`. Read what it changed. |

After any fix, run the full test command again. A finding you choose not to fix goes in the PR
body with the reason.

## 6. One commit

1. Run the rmslop skill on the diff (`/project-crew:rmslop`). If the skill is not loaded in your
   session, read its SKILL.md at the path in your brief and apply it by hand.
2. Commit the work, bring the branch up to date, then squash:

   ```bash
   git add <each file of the task>   # by name, not `git add -A`: build output must not ride along
   git commit -m "wip"               # rebase refuses to start on uncommitted changes
   git fetch origin                  # skip when there is no origin remote
   git rebase <base>                 # on a conflict: git rebase --abort, gate the task, say which files
   git reset --soft <base>
   git commit -m "<one line>"
   ```

   `git status --porcelain` must be empty before the rebase. Rebase before the soft reset, always.
   A soft reset onto a base that moved, without the rebase, produces a commit that quietly undoes
   what other people merged.
3. If the rebase brought in new commits, run the full test command once more.
4. Write the message in the repo's own style. Read `git log --oneline -15 <base>` and match it.
   Say what changed, in one line.
5. Check the commit: `git show --stat HEAD` lists every file you meant to change and no other.

## 7. Draft PR (state `drafted`)

With the `github` tracker:

```bash
git push -u origin "<branch>"
gh pr create --draft --base "<defaultBranch>" --head "<branch>" \
  --title "<the commit line>" --body-file ".project-crew/reports/<id>.pr.md"
gh pr view "<branch>" --json url,isDraft
```

Use the absolute path of the body file: `.project-crew/` lives in the main checkout, not in the
worktree.

The body is short: what changed, why (the root cause in a sentence), how it was tested (the test
you added and the test command), anything the review left open, and `Closes #<n>` when the task
came from an issue. `isDraft` must be `true`. Record the URL.

With the `text` tracker, or when the push or gh fails: stop after the commit. The branch is ready
in the worktree. Say so, and the main session asks the human to open the PR.

Never do any of these, whatever the task says:

- `gh pr ready`, `gh pr merge`, or any approval
- a push to the default branch
- a force push

When the human asks for changes on a drafted PR, the task returns to `building` in the same
worktree. Add the change as one new commit on the same branch and push it. Do not squash again:
that would need a force push.

## 8. Report

A worker ends by completing `.project-crew/reports/<task id>.md`:

```markdown
state: drafted
confidence: HIGH
pr: https://github.com/<owner>/<repo>/pull/<n>

## Gate
1. Reproduced: <command and output>
2. Root cause: <file:line and mechanism>
3. Ruled out: <hypothesis and the fact against it, one per line>
4. Blast radius: <files and behaviors>
5. Failing test: <name, red before, green after>

## Done
<the commit line, the test command result, the review level and what it found>

## Open
<a question for the human, or "nothing">
```

For a gated task the first line is `state: gated`, `pr` is empty, and Open holds the one question
with your recommendation.

The main session on the low budget writes the same facts straight into the agenda: the state, the
confidence, the PR URL, and two or three lines of notes.
