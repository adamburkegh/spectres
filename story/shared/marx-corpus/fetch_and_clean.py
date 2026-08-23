#!/usr/bin/env python
"""
One-off tool (not part of build.sh/build.ps1) that downloads the 33
chapters of Marx's Capital, Volume One from marxists.org (public domain --
Marx died 1883) and writes a cleaned, paragraph-per-blank-line plain text
corpus to capital-vol1.txt, committed alongside this script.

Run manually, occasionally -- e.g. when adding another volume, or fixing
the extraction. Rerunning overwrites capital-vol1.txt.

Usage:
    python story/shared/marx-corpus/fetch_and_clean.py
"""
import re
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

BASE_URL = "https://www.marxists.org/archive/marx/works/1867-c1/"
CHAPTERS = [f"ch{n:02d}.htm" for n in range(1, 34)]
OUT_PATH = Path(__file__).parent / "capital-vol1.txt"
USER_AGENT = "spectres-corpus-builder/1.0 (public-domain text corpus for a Twine game)"

# Paragraph classes that are footnotes/transcription-credits, front-matter
# table-of-contents, page title, or the nav footer -- not article prose.
SKIP_P_CLASSES = {"information", "toc", "index", "title", "footer"}
SKIP_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "script", "style", "table", "title"}


class ChapterExtractor(HTMLParser):
    """
    Extracts article prose paragraphs from a marxists.org chapter page,
    dropping headers, footnotes, transcription credits, nav/TOC chrome,
    <table> content (algebraic examples), and paragraphs that are
    entirely internal '#anchor' links (in-page outline lists that reuse
    the same CSS classes as real indented prose, so class-filtering alone
    can't tell them apart).
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip_stack = []
        self.internal_link_depth = 0
        self.buf = []
        self.plaintext_len = 0
        self.paragraphs = []

    def flush(self):
        text = "".join(self.buf)
        total_len = len(text)
        text = re.sub(r"\s+", " ", text).strip()
        # Majority (not just nonzero) of the paragraph's characters must be
        # outside internal links -- numbered outline items like
        # '1. <a href="#...">Title</a>' have a tiny bit of plain text
        # ("1. ") outside the link, so a nonzero check alone doesn't
        # catch them.
        if text and total_len > 0 and self.plaintext_len / total_len > 0.5:
            self.paragraphs.append(text)
        self.buf = []
        self.plaintext_len = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in SKIP_TAGS:
            self.skip_stack.append(tag)
            return
        if tag == "p" and attrs.get("class") in SKIP_P_CLASSES:
            self.skip_stack.append(tag)
            return
        if tag in ("p", "hr") and not self.skip_stack:
            self.flush()
        if tag == "a" and not self.skip_stack and attrs.get("href", "").startswith("#"):
            self.internal_link_depth += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if self.skip_stack and self.skip_stack[-1] == tag:
            self.skip_stack.pop()
            return
        if tag == "a" and self.internal_link_depth > 0:
            self.internal_link_depth -= 1

    def handle_data(self, data):
        if self.skip_stack:
            return
        self.buf.append(data)
        if self.internal_link_depth == 0:
            self.plaintext_len += len(data)

    def close(self):
        self.flush()
        super().close()


def clean_chapter(html: str) -> list[str]:
    extractor = ChapterExtractor()
    extractor.feed(html)
    extractor.close()
    cleaned = []
    for para in extractor.paragraphs:
        para = re.sub(r"\s*\[\d+\]", "", para)  # inline footnote markers, e.g. "sucks. [4]"
        para = re.sub(r"\s+", " ", para).strip()
        if para:
            cleaned.append(para)
    return cleaned


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req) as resp:
        raw = resp.read()
    return raw.decode("iso-8859-1")  # marxists.org pages declare this charset


def main():
    all_paragraphs = []
    for chapter_file in CHAPTERS:
        url = BASE_URL + chapter_file
        print(f"Fetching {url}")
        html = fetch(url)
        paragraphs = clean_chapter(html)
        all_paragraphs.append(f"# {chapter_file}")
        all_paragraphs.extend(paragraphs)
        time.sleep(0.5)  # be polite to marxists.org

    OUT_PATH.write_text("\n\n".join(all_paragraphs) + "\n", encoding="utf-8")
    print(f"Wrote {len(all_paragraphs)} paragraphs (incl. chapter markers) to {OUT_PATH}")


if __name__ == "__main__":
    main()
