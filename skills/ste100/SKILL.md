---
name: ste100
description: Writes or rewrites text to the rules of ASD-STE100 Simplified Technical English (STE), or reviews text against them, and checks the result with a linter. Short sentences, one meaning for each word, active voice, no idiom, and facts and code kept exactly. Use when asked to "write this in STE", "simplified technical english", "ASD-STE100", or "make this clear for a non-native reader".
argument-hint: "<text | file path | review <text or path>> [--diff]"
---

# ste100

Simplified Technical English (STE) is a controlled form of English for technical text. A reader
with limited English can read an STE text and find only one meaning in it. This skill writes text
to the STE rules and checks the structure of the text with a linter.

## Input

`$ARGUMENTS` is one of these:

- Text, or the path of a file: rewrite it and return the new text.
- `review <text or path>`: change nothing. Return a table with 3 columns: sentence, rule, fix.
- Nothing: ask for the text in one sentence and stop.

With `--diff`, return a table with 3 columns: before, after, rule.

Rewrite only prose. Do not rewrite code, quotations, stories or advertisements.

## Step 1: Set the type of each passage

- Procedure: text that tells the reader to do something. Each sentence has 20 words or less and
  gives one instruction.
- Description: text that explains. Each sentence has 25 words or less and gives one new fact.

## Step 2: Set the mode

- Pragmatic is the default. Apply all rules of structure. Keep the technical names and technical
  verbs that the reader knows, for example product names, file names, field names and identifiers.
- Strict applies when the request names STE or ASD-STE100. Also replace each word in
  `references/substitutions.md`. Tell the user one time that full compliance needs the official
  dictionary, which is free at https://www.asd-ste100.org/.

## Step 3: Write to the rules

The numbers refer to ASD-STE100 Issue 9.

| Topic | Rule |
|---|---|
| Words (1.1 to 1.14) | Use the short, common word. Give each word one meaning. Use one name for one item, each time. Do not use slang, idiom or metaphor. |
| Abbreviations (2.2) | At the first use, write the full name and then the abbreviation in parentheses. |
| Noun clusters (2.1) | Put 3 nouns or less in a row. Divide a longer cluster with of, for or in. |
| Verb forms (3.1 to 3.5) | Use the simple present, simple past, future, imperative and infinitive. Use a past participle only as an adjective. Do not use an -ing form, except in a technical name. |
| Voice (3.6) | Use the active voice. The passive voice is permitted only when the agent is not known. |
| Modal verbs | Use `can` for a possibility and `must` for a requirement. Do not use may, might, should, could or would. |
| Sentences (4.1 to 4.5) | Give each sentence one topic. Keep the articles and the word `that`. Do not use contractions. |
| Lists (4.3, 8.4) | Put a sequence or a set of options in a vertical list. Put a sentence that ends with a colon before the list. |
| Procedures (5.1 to 5.5) | Write each instruction as a command. Put the condition first, then the command. A note gives information, not an instruction. |
| Paragraphs (6.4 to 6.6) | Give each paragraph one topic and 6 sentences or less. Put the topic sentence first. |
| Risk words (7.1 to 7.3) | Use WARNING only for a risk of injury. Use CAUTION only for a risk of damage. Give the command first, then the risk. |
| Punctuation (8.1 to 8.3) | Do not use semicolons or em dashes. Do not use a slash between alternatives. Do not put necessary information in parentheses. |
| Numbers | Write numbers as digits. Write "about" before an estimate. |

Example of a procedure:

```text
Before: Prior to restarting the server, the config file should be backed up; otherwise settings may be lost.
After:  Make a copy of the configuration file. Then start the server again.
        CAUTION: Do not start the server again before you make the copy. If you do, you can lose the settings.
```

## Step 4: Keep the facts

- Do not add, remove or weaken a fact, a number, a condition or a requirement.
- Copy code, identifiers, paths, commands, log lines and error text exactly.
- If a sentence changes its meaning when you rewrite it, keep the sentence. Put it in a
  "Kept as-is:" list with the reason.

## Step 5: Run the linter

1. Write your text to a temporary file.
2. Make an allow file. Put each technical name of the text on its own line.
3. Run the linter. Use `--mode procedural` for a procedure and `--mode descriptive` for all other
   text.
4. Correct each finding that you can correct.
5. For each finding that you cannot correct, give one line with the reason.

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/ste_check.py" --mode descriptive --allow /tmp/ste-allow.txt /tmp/ste-draft.md
```

The linter exits with 1 when it finds an error. Add `--json` for output that a program can read.

| Finding | Meaning |
|---|---|
| `LEN` | the sentence is longer than the limit of the mode |
| `PARA` | the paragraph has more than 6 sentences |
| `ING` | an -ing form |
| `MODAL` | may, might, should, could or would |
| `PASSIVE` | a form of "be" before a past participle |
| `SEMI`, `DASH`, `SLASH` | a semicolon, an em dash, or a slash between alternatives |
| `ABBR` | an abbreviation with no definition, or a use before the definition |
| `WORD` | a word from `references/substitutions.md` |
| `CLUSTER` | 4 or more nouns in a row, as a warning |

## Output

Return only the text. A "Kept as-is:" list can follow it. Do not tell the user that the text is
certified or compliant. If the user asks, say that you wrote the text to STE rules.

## Limits

The linter checks structure and the word list in `references/substitutions.md`. It does not know
the ASD dictionary. It finds a noun cluster only when each noun starts with a capital letter. It
cannot count the instructions in a sentence, and it cannot tell if a word has 2 meanings. You
must do these checks.

ASD-STE100 is a trademark of the Aerospace, Security and Defence Industries Association of Europe
(ASD). This skill is not official. It does not contain the ASD dictionary and it does not certify
compliance. The rule numbers follow the public rule catalog of the MIT-licensed
`AminBlg/SimpleEnglish` skill.
