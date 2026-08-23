#!/usr/bin/env python
"""
One-off tool (not part of build.sh/build.ps1) that splits the cleaned
corpus (capital-vol1.txt, see fetch_and_clean.py) into sentence-level
candidates and filters them down to ones that read reasonably as a
standalone quote, then overwrites story/shared/marx-quotes.txt -- the
plain-text, one-quote-per-line file build.sh/build.ps1 already compile
into the game's "Marx Quotes" data passage.

This step is fully automatic (no manual curation pass): the filters
below are heuristics, not a guarantee every line reads well out of
context -- see the discussion in the project history for that tradeoff.

Run manually, occasionally -- e.g. after re-running fetch_and_clean.py,
or to retune the filters. Rerunning overwrites marx-quotes.txt.

Usage:
    python story/shared/marx-corpus/extract_quotes.py
"""
import re
from pathlib import Path

CORPUS_PATH = Path(__file__).parent / "capital-vol1.txt"
OUT_PATH = Path(__file__).parent.parent / "marx-quotes.txt"

MIN_WORDS = 8
MAX_WORDS = 35

SENTENCE_RE = re.compile(r"[^.!?]*[.!?]")
# Runs of 2+ periods (with or without spaces between, e.g. "..." or ". . .")
# mark omitted material in the source text, not a sentence end -- treat them
# as a hard break so the sentence regex above doesn't stop at their first dot.
ELLIPSIS_RE = re.compile(r"\.\s*\.[.\s]*")

HEADER = """\
# Source data for the Marx's Ghost mechanic (see marx.twee).
# One quote per line. Blank lines and lines starting with # are ignored.
# Public domain (Marx died 1883). Source: marxists.org, Capital Vol. 1.
#
# GENERATED FILE -- do not hand-edit. Produced by
# story/shared/marx-corpus/extract_quotes.py from capital-vol1.txt.
# To change the quote pool, edit the corpus or the filters in that
# script and rerun it (see story/shared/marx-corpus/fetch_and_clean.py
# and extract_quotes.py for the full pipeline).
"""


def looks_quotable(sentence: str) -> bool:
    words = sentence.split()
    if not (MIN_WORDS <= len(words) <= MAX_WORDS):
        return False
    if not sentence[-1] in ".!?":
        return False
    if not re.match(r'^[A-Z"“]', sentence):
        return False  # reject fragments starting with a closing quote (’/”) --
        # those are the tail of a quotation that began earlier, not a standalone one
    if len(re.findall(r"\d+", sentence)) >= 2:
        return False  # likely a numeric example/table remnant
    if sentence.count("—") >= 3 or sentence.count("--") >= 3:
        return False  # likely leftover algebraic notation (A---B---C)
    if len(re.findall(r"(?:^|\s)[A-Z](?:\s|$)", sentence)) >= 2:
        return False  # likely algebra using single-letter variables
    return True


def extract_sentences(paragraph: str) -> list[str]:
    sentences = []
    for chunk in ELLIPSIS_RE.split(paragraph):
        sentences.extend(m.group().strip() for m in SENTENCE_RE.finditer(chunk))
    return sentences


def main():
    text = CORPUS_PATH.read_text(encoding="utf-8")
    paragraphs = [p for p in text.split("\n\n") if p.strip() and not p.startswith("#")]

    seen = set()
    quotes = []
    for para in paragraphs:
        para = para.replace("\n", " ")
        for sentence in extract_sentences(para):
            sentence = re.sub(r"\s+", " ", sentence).strip()
            if sentence in seen:
                continue
            if looks_quotable(sentence):
                seen.add(sentence)
                quotes.append(sentence)

    body = "\n".join(quotes) + "\n"
    OUT_PATH.write_text(HEADER + "\n" + body, encoding="utf-8")
    print(f"Wrote {len(quotes)} quotes to {OUT_PATH}")


if __name__ == "__main__":
    main()
