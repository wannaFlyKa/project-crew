#!/usr/bin/env python3
"""Structural linter for ASD-STE100 style text. Standard library only.

Usage:
  ste_check.py [--mode procedural|descriptive] [--allow FILE] [--json]
               [--baseline N] <file | ->

It checks the mechanical rules only (length, verb forms, punctuation,
abbreviations, the house word list). It does not know the ASD dictionary and
does not certify compliance. ASD-STE100 is a trademark of ASD.

Markdown handling: fenced code blocks and YAML frontmatter are skipped. Inline
code, URLs and quoted strings each count as one word and are not inspected.
Headings and table rows get the word-level checks but not the length checks.
An abbreviation counts as defined if its definition is in the same paragraph.
Only errors count toward --baseline; CLUSTER is a warning.

Rule numbers follow the Issue 9 catalog of the MIT-licensed AminBlg/SimpleEnglish
skill. No code from that skill or from danyuchn/asd-ste100-skill is used.
"""

import argparse
import json
import re
import sys
from pathlib import Path

LIMITS = {"procedural": 20, "descriptive": 25}
MAX_SENTENCES = 6

# rule id -> (severity, STE reference, fix hint)
RULES = {
    "LEN": ("error", "5.1/6.3", "split the sentence, one topic each"),
    "PARA": ("error", "6.6", "split the paragraph at a change of topic"),
    "ING": ("error", "3.5", "use a simple tense or a noun; allow with --allow if it is a technical name"),
    "MODAL": ("error", "dictionary", "use can (possibility) or must (requirement)"),
    "PASSIVE": ("error", "3.6", "name the agent and use the active voice, or keep only if the agent is unknown"),
    "SEMI": ("error", "8.1", "end the sentence or use a comma"),
    "DASH": ("error", "house", "use a comma, a period or a colon"),
    "SLASH": ("error", "house", "write 'or', 'and', or both words"),
    "ABBR": ("error", "2.2/8.3", "write the full name, then the abbreviation in parentheses, at first use"),
    "WORD": ("error", "dictionary", "use the approved word"),
    "CLUSTER": ("warning", "2.1", "split the noun cluster with of, for or in, or define it as one technical name"),
}

MODALS = re.compile(r"\b(may|might|should|could|would)\b", re.I)
MAY_AFTER_MONTH = re.compile(r"\s*(?:\d|[,.;:!?)]|$)")


def is_month_may(text, m):
    """Lowercase may is the modal. May or MAY before a digit or punctuation is the
    month, and so is title-case May in the middle of a sentence."""
    word = m.group(1)
    if word == "may":
        return False
    if MAY_AFTER_MONTH.match(text, m.end()):
        return True
    before = text[:m.start()].rstrip()
    return word == "May" and bool(before) and before[-1] not in ".!?:"


ING_NOUNS = {
    "thing", "anything", "everything", "nothing", "something", "string", "during",
    "bring", "sting", "swing", "cling", "sling", "fling",
    "setting", "meeting", "building", "morning", "evening", "spring", "ceiling",
    "warning", "heading", "finding", "ending", "sibling", "meaning", "offspring",
}
ING_WORD = re.compile(r"\b([A-Za-z]{2,}ing)\b")

BE = r"(?:am|is|are|was|were|be|been|being)"
ADVERB = r"(?:[a-z]+ly|not|also|then|now|often|never|still|already|always|only|first|again|both|all|each|being|too|well|later|sometimes|once|yet)"
IRREGULAR = (
    "done|made|given|taken|written|built|sent|set|put|run|kept|left|found|held|"
    "shown|known|seen|lost|read|cut|hit|met|paid|said|sold|told|thought|bought|"
    "brought|caught|taught|chosen|driven|forgotten|frozen|hidden|spoken|stolen|"
    "broken|begun|won|gone|got|gotten|led|fed|bound|split|spread|dealt|meant|"
    "felt|hurt|cost|let|shut|lit|lent|bent|spent|torn|worn|drawn|thrown|grown|"
    "blown|flown|understood|withdrawn|rewritten|overridden|reset|rerun|"
    "undone|redone|upheld|withheld|sewn|woven|proven|risen|striven|born|"
    "swept|dug|fought|sought|struck|stuck|slid|sung|sunk|shrunk|bitten|eaten|"
    "beaten|redrawn"
)
PASSIVE = re.compile(
    rf"\b({BE})(?:\s+{ADVERB}){{0,2}}\s+([A-Za-z]{{3,}}ed|{IRREGULAR})\b", re.I
)
NOT_PARTICIPLE = {
    "indeed", "speed", "exceed", "proceed", "succeed", "hundred", "naked",
    "wicked", "sacred", "rugged", "unused", "embed", "agreed", "greed", "creed",
    "breed",
}

ABBR = re.compile(r"(?<![\w-])([A-Z]{2,6})(?:s|'s)?(?![\w-])")
ABBR_PAREN_DEF = re.compile(r"\(([A-Z]{2,6})s?\)")
ABBR_LEADS_DEF = re.compile(r"(?<![\w-])([A-Z]{2,6})s?\s*\(([^()]*[a-z][^()]*)\)")
ABBR_TABLE_DEF = re.compile(r"^\s*\|\s*([A-Z]{2,6})\s*\|\s*[^|]*[a-z][^|]*\|", re.M)
ABBR_IGNORE = {"WARNING", "CAUTION", "NOTE", "OK", "II", "III", "IV", "VI", "VII", "VIII", "IX", "XI", "XII"}

LEADING = {"a", "an", "the", "this", "that", "these", "those", "each", "all", "if", "when", "then", "use", "set", "run", "open", "see", "note"}
CLUSTER = re.compile(r"(?<![\w-])((?:[A-Z][A-Za-z0-9]*\s+){3,}[A-Z][A-Za-z0-9]*)(?![\w-])")

SLASH_TOKEN = re.compile(r"^[A-Za-z]+/[A-Za-z]+[.,:!?]?$")
SPACED_SLASH = re.compile(r"\w\s+/\s+\w")
EM_DASH = re.compile(r"—|\s–\s|\s--\s")

INLINE_CODE = re.compile(r"`[^`\n]+`")
URL = re.compile(r"(?:https?|ftp)://[^\s<>()\"]*[^\s<>()\".,:;!?]")
QUOTED = re.compile(r"\"[^\"\n]+\"")
LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
EMPHASIS = re.compile(r"\*\*|__|(?<!\w)\*(?!\s)|(?<!\s)\*(?!\w)")
LIST_MARK = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
TABLE_ROW = re.compile(r"^\s*\|")
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{2,}")
FENCE = re.compile(r"^\s*(```|~~~)")
SENTENCE_END = re.compile(r"(?<=[.!?:])\s+(?=[A-Z0-9\"'(\[_]|codeword|urlword|quotedword)")
TERMINAL = re.compile(r"[.!?:]\s*$")


def load_lines(path):
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    return text.splitlines()


def load_allow(path):
    if not path:
        return set()
    words = set()
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        word = raw.strip()
        if word and not word.startswith("#"):
            words.add(word.lower())
    return words


def load_substitutions():
    """Parse references/substitutions.md: table rows '| bad | good |'."""
    path = Path(__file__).resolve().parent.parent / "references" / "substitutions.md"
    if not path.exists():
        print(f"warning: {path} not found; WORD check skipped", file=sys.stderr)
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or TABLE_SEP.match(line):
            continue
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0].lower() == "not ste":
            continue
        bad, good = cells[0], cells[1]
        if bad:
            entries.append((bad, good))
    return entries


def inflect(word):
    """Common inflections of one word; literal match for tokens with punctuation."""
    w = re.escape(word)
    if not word.isalpha():
        return [w]
    last = re.escape(word[-1])
    forms = [w, w + "s", w + "es", w + "ed", w + "d", w + "ing", w + last + "ed", w + last + "ing"]
    if word.endswith("e"):
        forms.append(re.escape(word[:-1]) + "ing")
    if word.endswith("y"):
        stem = re.escape(word[:-1])
        forms += [stem + "ies", stem + "ied"]
    return forms


def word_pattern(phrase):
    """Match the phrase with an inflected first word and an optional plural last word."""
    words = phrase.lower().split()
    head = "(?:" + "|".join(inflect(words[0])) + ")"
    rest = "".join(r"\s+" + re.escape(x) for x in words[1:])
    tail = "s?" if len(words) > 1 and words[-1].isalpha() else ""
    return re.compile(r"(?<![\w-])" + head + rest + tail + r"(?![\w-])", re.I)


class Block:
    """A unit of prose: paragraph, list item, heading or table row."""

    def __init__(self, kind, line_no):
        self.kind = kind
        self.line_no = line_no
        self.lines = []
        self.numbers = []

    def append(self, line_no, line):
        self.lines.append(line)
        self.numbers.append(line_no)

    def text(self):
        return " ".join(l.strip() for l in self.lines)

    def locate(self, span):
        """Line number of the first line that holds the start of the span."""
        words = span.split()
        if len(self.lines) > 1 and words:
            for no, line in zip(self.numbers, self.lines):
                if words[0] in line:
                    return no
        return self.line_no


def strip_frontmatter(lines):
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return [""] * (i + 1) + lines[i + 1:]
    return lines


def blocks_from(lines):
    """Group lines into blocks; drop fenced code and HTML comments."""
    blocks, current, in_fence, in_comment = [], None, None, False
    for idx, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        fence = FENCE.match(line)
        if in_fence:
            if fence and fence.group(1) == in_fence:
                in_fence = None
            continue
        if fence:
            in_fence = fence.group(1)
            current = None
            continue
        if in_comment:
            if "-->" in line:
                in_comment = False
                line = line.split("-->", 1)[1]
            else:
                continue
        if "<!--" in line and "-->" not in line:
            in_comment = True
            line = line.split("<!--", 1)[0]
        line = HTML_COMMENT.sub("", line)
        line = re.sub(r"^\s{0,3}>\s?", "", line)
        if not line.strip():
            current = None
            continue
        if HEADING.match(line):
            blocks.append(Block("heading", idx))
            blocks[-1].append(idx, HEADING.sub("", line))
            current = None
        elif TABLE_ROW.match(line):
            if not TABLE_SEP.match(line):
                blocks.append(Block("table", idx))
                blocks[-1].append(idx, line)
            current = None
        elif LIST_MARK.match(line):
            current = Block("item", idx)
            current.append(idx, LIST_MARK.sub("", line))
            blocks.append(current)
        else:
            if current is None:
                current = Block("para", idx)
                blocks.append(current)
            current.append(idx, line)
    return blocks


def clean(text):
    """Replace protected spans with one-word placeholders, strip markup."""
    text = LINK.sub(r"\1", text)
    text = INLINE_CODE.sub(" codeword ", text)
    text = URL.sub(" urlword ", text)
    text = QUOTED.sub(" quotedword ", text)
    text = EMPHASIS.sub("", text)
    return text


def split_sentences(text):
    parts = SENTENCE_END.split(text)
    return [p.strip() for p in parts if p.strip()]


def count_words(sentence):
    return len([t for t in sentence.split() if re.search(r"[A-Za-z0-9]", t)])


class Checker:
    def __init__(self, mode, allow, subs):
        self.limit = LIMITS[mode]
        self.allow = allow
        self.subs = [(good, word_pattern(bad)) for bad, good in subs]
        self.findings = []

    def add(self, where, rule, span, hint=None):
        line_no = where.locate(span) if isinstance(where, Block) else where
        severity, ref, default_hint = RULES[rule]
        self.findings.append({
            "line": line_no, "rule": rule, "severity": severity, "ste": ref,
            "span": span, "hint": hint or default_hint,
        })

    def allowed(self, word):
        return word.lower() in self.allow

    def run(self, lines):
        lines = strip_frontmatter(lines)
        blocks = blocks_from(lines)
        for b in blocks:
            self.check_block(b)
        self.check_abbreviations(blocks)
        return self.findings

    def check_block(self, b):
        text = clean(b.text())
        for m in EM_DASH.finditer(text):
            self.add(b, "DASH", m.group(0).strip() or "em dash")
        if ";" in text:
            self.add(b, "SEMI", ";")
        for tok in text.split():
            if SLASH_TOKEN.match(tok) and not self.allowed(tok.rstrip(".,:!?")):
                self.add(b, "SLASH", tok)
        if SPACED_SLASH.search(text):
            self.add(b, "SLASH", "/")
        for m in MODALS.finditer(text):
            if m.group(1).lower() == "may" and is_month_may(text, m):
                continue
            self.add(b, "MODAL", m.group(1))
        for m in ING_WORD.finditer(text):
            w = m.group(1)
            if w.lower() in ING_NOUNS or self.allowed(w):
                continue
            self.add(b, "ING", w)
        for m in PASSIVE.finditer(text):
            part = m.group(2)
            if part.lower() in NOT_PARTICIPLE or self.allowed(part):
                continue
            self.add(b, "PASSIVE", m.group(0))
        for good, pat in self.subs:
            for m in pat.finditer(text):
                if self.allowed(m.group(0)):
                    continue
                self.add(b, "WORD", m.group(0), f"use '{good}'")
        if b.kind in ("heading", "table"):
            return
        for m in CLUSTER.finditer(text):
            words = m.group(1).split()
            while words and words[0].lower() in LEADING:
                words.pop(0)
            if len(words) >= 4:
                self.add(b, "CLUSTER", " ".join(words))
        if b.kind == "item" and not TERMINAL.search(text) and count_words(text) <= 8:
            return
        sentences = split_sentences(text)
        if b.kind == "para" and len(sentences) > MAX_SENTENCES:
            self.add(b, "PARA", f"{len(sentences)} sentences")
        for s in sentences:
            words = count_words(s)
            if words > self.limit:
                self.add(b, "LEN", s[:60] + ("..." if len(s) > 60 else ""),
                         f"{words} words, limit {self.limit}")

    def check_abbreviations(self, blocks):
        """Flag the first body use of an abbreviation that has no definition, or
        that comes in a paragraph before the paragraph with its definition."""
        defined_at, any_def, uses = {}, set(), []
        for i, b in enumerate(blocks):
            text = clean(b.text())
            for m in ABBR_TABLE_DEF.finditer(text):
                any_def.add(m.group(1))
            for rx in (ABBR_PAREN_DEF, ABBR_LEADS_DEF):
                for m in rx.finditer(text):
                    any_def.add(m.group(1))
                    defined_at.setdefault(m.group(1), i)
            if b.kind == "heading":
                continue
            for m in ABBR.finditer(text):
                a = m.group(1)
                if a not in ABBR_IGNORE and not self.allowed(a):
                    uses.append((a, i, b.locate(a)))
        seen = set()
        for a, i, line_no in uses:
            if a in seen:
                continue
            seen.add(a)
            if a not in any_def:
                self.add(line_no, "ABBR", a, f"no definition in the text; write the full name, then ({a})")
            elif a in defined_at and i < defined_at[a]:
                self.add(line_no, "ABBR", a, "used before its definition; define it at first use")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="file to check, or - for stdin")
    ap.add_argument("--mode", choices=sorted(LIMITS), default="descriptive",
                    help="sentence limit: procedural 20 words, descriptive 25 (default)")
    ap.add_argument("--allow", metavar="FILE", help="technical names, one per line; exempt from ING, PASSIVE, ABBR, WORD and SLASH")
    ap.add_argument("--json", action="store_true", help="emit findings as a JSON array")
    ap.add_argument("--baseline", type=int, default=0, metavar="N", help="exit 1 only when errors exceed N (default 0)")
    args = ap.parse_args()

    checker = Checker(args.mode, load_allow(args.allow), load_substitutions())
    findings = checker.run(load_lines(args.path))
    findings.sort(key=lambda f: (f["line"], f["rule"], f["span"]))
    errors = sum(1 for f in findings if f["severity"] == "error")
    warnings = len(findings) - errors

    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        for f in findings:
            flag = "W" if f["severity"] == "warning" else "E"
            print(f'{f["line"]}: {f["rule"]} [{flag}] "{f["span"]}" -> {f["hint"]} (STE {f["ste"]})')
        print(f"{errors} errors, {warnings} warnings (mode {args.mode}, baseline {args.baseline})")
    sys.exit(1 if errors > args.baseline else 0)


if __name__ == "__main__":
    main()
