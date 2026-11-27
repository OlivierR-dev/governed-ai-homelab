#!/usr/bin/env python3
"""Style linter for posts and articles.

Implements section 4 of docs/style-guide.md. Standard library only.

Blocking rules (exit code 1):
  dash                  em dash or en dash
  announcement          announcement / wrap-up formulas from the guide
  inflated-word         inflated vocabulary from the guide
  emoji-line-start      emoji at the start of a line or list item
  multiple-punctuation  !!, ??, ?!, !?

Warnings (reported, exit code unchanged):
  rhetorical-question   question followed by a short answer, end of paragraph
  short-paragraphs      more than 2 one-line paragraphs under 8 words
  length                post 120-250 words, article 600-1200 words
  parentheses           more than 2 parentheses in a paragraph

Fenced code blocks and inline code are ignored.

Exit codes: 0 no blocking finding, 1 at least one blocking finding,
2 usage error (no file, unreadable file).
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

BLOCKING = "BLOCKING"
WARNING = "WARNING"

APOSTROPHE = "['’]"


def _phrase(text: str) -> str:
    """Turn a plain phrase into a regex: flexible spaces and apostrophes."""
    parts = []
    for ch in text:
        if ch == "'":
            parts.append(APOSTROPHE)
        elif ch == " ":
            parts.append(r"\s+")
        else:
            parts.append(re.escape(ch))
    return r"(?<!\w)" + "".join(parts) + r"(?!\w)"


ANNOUNCEMENTS = [
    "spoiler",
    "plot twist",
    "et c'est là que",
    "le constat est simple",
    "soyons honnêtes",
    "laissez-moi vous expliquer",
    "voici pourquoi",
    "décryptage",
    "en résumé",
    "au final, ce qu'il faut retenir",
    "et ça change tout",
]
ANNOUNCEMENT_RE = [(a, re.compile(_phrase(a), re.IGNORECASE)) for a in ANNOUNCEMENTS]

INFLATED = [
    ("crucial", r"crucia(?:l|le|les|ux)"),
    ("essentiel", r"essentiel(?:le|les|s)?"),
    ("incontournable", r"incontournables?"),
    ("véritable", r"véritable(?:s|ment)?"),
    ("révolutionner", r"révolutionn\w*"),
    ("game changer", r"game[\s-]?changers?"),
    ("levier", r"leviers?"),
    ("paradigme", r"paradigmes?"),
    ("booster", r"boost\w*"),
    ("au cœur de", r"au\s+c(?:œ|oe)ur\s+d(?:e|u|es)"),
    ("dans un monde où", r"dans\s+un\s+monde\s+où"),
    ("à l'ère de", r"à\s+l" + APOSTROPHE + r"ère\s+d(?:e|u|es)"),
]
INFLATED_RE = [
    (label, re.compile(r"(?<!\w)" + rx + r"(?!\w)", re.IGNORECASE))
    for label, rx in INFLATED
]

DASH_RE = re.compile("[—–]")
MULTI_PUNCT_RE = re.compile(r"!!|\?\?|\?!|!\?")
EMOJI_CLASS = (
    "[\U0001F000-\U0001FAFF"  # pictographs, emoticons, transport, symbols
    "☀-➿"  # misc symbols, dingbats (check marks, etc.)
    "⌀-⏿"  # misc technical (hourglass, alarm clock)
    "⬀-⯿]"  # stars, squares
)
EMOJI_START_RE = re.compile(r"^\s*(?:[-*+>]\s+|\d+[.)]\s+)?" + EMOJI_CLASS)
RHETORICAL_RE = re.compile(r"\?\s+[A-ZÉ][^.?!]{0,40}\.\s*$")
WORD_RE = re.compile(r"\w+(?:['’-]\w+)*")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s")
LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
FENCE_RE = re.compile(r"^\s{0,3}(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")

LENGTH_LIMITS = {"post": (120, 250), "article": (600, 1200)}
SHORT_PARAGRAPH_WORDS = 8
SHORT_PARAGRAPH_MAX = 2
PARENTHESES_MAX = 2


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    level: str
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.level} [{self.rule}] {self.message}"


def strip_code(lines: List[str]) -> List[str]:
    """Blank out fenced code blocks and inline code, keeping line numbers."""
    out = []
    in_fence = False
    for line in lines:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        if in_fence:
            out.append("")
            continue
        out.append(INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), line))
    return out


def paragraphs(lines: List[str]) -> List[Tuple[int, List[str]]]:
    """Split into paragraphs: (1-based first line number, lines)."""
    result = []
    current: List[str] = []
    start = 0
    for number, line in enumerate(lines, 1):
        if line.strip():
            if not current:
                start = number
            current.append(line)
        elif current:
            result.append((start, current))
            current = []
    if current:
        result.append((start, current))
    return result


def is_heading(line: str) -> bool:
    return bool(HEADING_RE.match(line))


def is_hashtag_line(text: str) -> bool:
    tokens = text.split()
    return bool(tokens) and all(t.startswith("#") and len(t) > 1 for t in tokens)


def count_words(lines: Iterable[str]) -> int:
    total = 0
    for line in lines:
        if is_heading(line) or is_hashtag_line(line):
            continue
        total += len(WORD_RE.findall(line))
    return total


def guess_kind(path: Path) -> Optional[str]:
    parts = {p.lower() for p in path.parts}
    if "posts" in parts:
        return "post"
    if "articles" in parts:
        return "article"
    return None


def lint_text(text: str, path: str = "<text>", kind: Optional[str] = None) -> List[Finding]:
    findings: List[Finding] = []
    lines = strip_code(text.splitlines())

    def add(line: int, level: str, rule: str, message: str) -> None:
        findings.append(Finding(path, line, level, rule, message))

    # Line-level blocking rules.
    for number, line in enumerate(lines, 1):
        for match in DASH_RE.finditer(line):
            add(number, BLOCKING, "dash", f"dash {match.group(0)!r}: use a comma, a parenthesis or a full stop")
        for label, rx in ANNOUNCEMENT_RE:
            if rx.search(line):
                add(number, BLOCKING, "announcement", f"announcement formula: {label!r}")
        for label, rx in INFLATED_RE:
            match = rx.search(line)
            if match:
                add(number, BLOCKING, "inflated-word", f"inflated word: {match.group(0)!r} ({label})")
        if EMOJI_START_RE.match(line):
            add(number, BLOCKING, "emoji-line-start", "emoji at the start of a line")
        for match in MULTI_PUNCT_RE.finditer(line):
            add(number, BLOCKING, "multiple-punctuation", f"multiple punctuation {match.group(0)!r}")

    # Paragraph-level warnings.
    short = []
    for start, block in paragraphs(lines):
        body = [l for l in block if not is_heading(l)]
        if not body:
            continue
        joined = " ".join(l.strip() for l in body)
        last_line = start + len(block) - 1
        if RHETORICAL_RE.search(joined):
            add(last_line, WARNING, "rhetorical-question", "question followed by a short answer")
        if joined.count("(") > PARENTHESES_MAX:
            add(start, WARNING, "parentheses", f"{joined.count('(')} parentheses in one paragraph (max {PARENTHESES_MAX})")
        if (
            len(block) == 1
            and not LIST_RE.match(block[0])
            and not is_hashtag_line(joined)
            and len(WORD_RE.findall(joined)) < SHORT_PARAGRAPH_WORDS
        ):
            short.append(start)
    if len(short) > SHORT_PARAGRAPH_MAX:
        add(short[0], WARNING, "short-paragraphs",
            f"{len(short)} one-line paragraphs under {SHORT_PARAGRAPH_WORDS} words "
            f"(max {SHORT_PARAGRAPH_MAX}), lines {', '.join(map(str, short))}")

    if kind in LENGTH_LIMITS:
        low, high = LENGTH_LIMITS[kind]
        words = count_words(lines)
        if not low <= words <= high:
            add(1, WARNING, "length", f"{words} words, expected {low}-{high} for a {kind}")

    return findings


def collect(targets: List[str]) -> List[Path]:
    files: List[Path] = []
    for target in targets:
        p = Path(target)
        if p.is_dir():
            files.extend(sorted(f for f in p.rglob("*.md") if f.is_file()))
        elif p.is_file():
            files.append(p)
        else:
            raise FileNotFoundError(target)
    return files


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Style linter (docs/style-guide.md, section 4).")
    parser.add_argument("targets", nargs="+", help="Markdown files or directories")
    parser.add_argument("--kind", choices=["post", "article", "auto", "none"], default="auto",
                        help="length rule to apply; auto guesses from a posts/ or articles/ path")
    args = parser.parse_args(argv)

    try:
        files = collect(args.targets)
    except FileNotFoundError as exc:
        print(f"error: no such file or directory: {exc}", file=sys.stderr)
        return 2

    findings: List[Finding] = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"error: cannot read {f}: {exc}", file=sys.stderr)
            return 2
        kind = guess_kind(f) if args.kind == "auto" else (None if args.kind == "none" else args.kind)
        findings.extend(lint_text(text, str(f), kind))

    for finding in findings:
        print(finding)
    blocking = sum(1 for f in findings if f.level == BLOCKING)
    warnings = len(findings) - blocking
    print(f"{len(files)} file(s), {blocking} blocking, {warnings} warning(s)")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
