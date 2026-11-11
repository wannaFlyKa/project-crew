---
name: rmslop
description: Strips AI filler from a diff before it is committed - comments that repeat the code, narration of the change, padding in docs, code that guards against nothing, and vague commit messages. Use when asked to "remove slop", "clean up the diff" or "de-AI this change", and before any commit of AI-written code.
argument-hint: "[base ref, default: staged and unstaged changes]"
---

# rmslop

A diff written by a model often carries text and code that a careful engineer would not have
typed. This skill finds that filler in the pending change and cuts it. It changes only lines the
diff added. It does not restyle code that was already there.

## Scope

`$ARGUMENTS` can name a base ref. Then the diff is `git diff <base>...HEAD` plus uncommitted
changes. With no argument it is `git diff HEAD`, staged and unstaged together.

## What to cut

Comments

- A comment that says what the next line already says: `// increment the counter`,
  `# return the result`, `// constructor`.
- A label on a block that needs none: `// imports`, `// helper functions`, `// main logic`.
- The story of the change: "now handles", "previously this", "as requested", "fixed the bug
  where". That belongs in the commit, and the comment is wrong the day after the merge.
- A long block comment. Keep the one or two lines that say why, drop the rest.
- Notes to the reader of the chat: "Note:", "Important:", "This ensures that".

Code

- A variable used once, on the next line, whose name adds nothing.
- A check for a state the types or the caller already rule out.
- A `try` that catches an error only to log and rethrow it unchanged, or to swallow it.
- A wrapper function with one caller and one line.
- Options, parameters or config keys that nothing uses yet.
- Leftover debug output and commented-out code.
- Formatting or renames in lines the task did not need to touch. Revert those hunks.

Docs and docstrings

- A parameter or return line that repeats the name: `@param user the user`.
- Openers such as "This function is responsible for". Start with the verb.
- A new README section or doc file that the task did not ask for.

Commit message

- A line that could describe any commit: "Update code", "Fix bug", "Improve readability". Name
  the thing that changed.
- A body that walks through the files. The diff already does.

## What to keep

- A comment that gives a reason the code cannot show: a workaround, an ordering constraint, a
  link to the bug it guards against.
- Doc comments on a public interface, where the project writes them.
- Checks at a real boundary: user input, the network, the file system.
- Anything the project's linter or style guide requires.
- Every line the diff did not add.

When you cannot tell if a line is filler, keep it and list it.

## Steps

1. Read the diff once, whole.
2. Cut each instance. Make no other change.
3. If you removed or changed code, not only comments, run the project's tests again.
4. Report in this shape:

```markdown
Cut
- src/cache.py:41 comment repeated the function name
- src/cache.py:58-61 try block that only rethrew
- tests/test_cache.py:9 debug print

Kept
- src/cache.py:73 comment explains the eviction order
```

If there was nothing to cut, say "No slop found." and stop.
