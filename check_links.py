#!/usr/bin/env python
"""
Deterministic, static check of the story/ passage graph -- no browser, no
Tweego, no tokens. Checks:

  1. Every [[link]] target actually exists as a defined passage.
  2. Every normal content passage is reachable from the configured start
     passage (StoryData "start") via the link graph.

Link targets that look like TwineScript variables (start with $ or _,
e.g. a widget's [[_char.display->_char.target]]) are dynamic and can't be
resolved statically -- they're reported separately, not treated as broken.

This does NOT replace the browser-driven checks: it has no idea whether a
[script] passage is valid JavaScript, whether a widget renders the right
text, or whether randomized logic behaves correctly. It only checks the
shape of the passage graph.

Usage:
    python check_links.py
Exit code is nonzero if any broken (non-dynamic) link is found.
"""
import re
import sys
from pathlib import Path

STORY_DIR = Path(__file__).parent / "story"
STORY_DATA_FILE = STORY_DIR / "config" / "00-story-data.twee"

# Passages that are SugarCube special machinery, not navigable content --
# excluded from the "must be reachable from Start" check.
SPECIAL_PASSAGE_NAMES = {
    "StoryData", "StoryTitle", "StoryInit", "StoryCaption", "StoryMenu",
    "StoryShare", "StoryDisplayTitle", "StorySubtitle", "StoryBanner",
    "StoryAuthor", "StoryInterface", "PassageHeader", "PassageFooter",
    "PassageDone", "StoryStylesheet", "StoryJavaScript",
}
SPECIAL_TAGS = {"script", "stylesheet", "widget", "data"}

PASSAGE_HEADER_RE = re.compile(r"^::\s*([^\[\{]+?)\s*(?:\[([^\]]*)\])?\s*(?:\{.*\})?\s*$")
LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
DYNAMIC_TARGET_RE = re.compile(r"^[$_]")  # TwineScript variable sigils


def parse_link_target(raw: str) -> str:
    raw = raw.split("][", 1)[0]  # drop a trailing setter, e.g. "Target][$x = 1]"
    if "->" in raw:
        return raw.split("->", 1)[1].strip()
    if "<-" in raw:
        return raw.split("<-", 1)[0].strip()
    if "|" in raw:
        return raw.split("|", 1)[1].strip()
    return raw.strip()


def find_start_passage() -> str:
    text = STORY_DATA_FILE.read_text(encoding="utf-8")
    m = re.search(r'"start"\s*:\s*"([^"]+)"', text)
    if not m:
        raise SystemExit(f"Could not find \"start\" in {STORY_DATA_FILE}")
    return m.group(1)


def main():
    twee_files = sorted(STORY_DIR.rglob("*.twee"))

    passages = {}  # name -> (file, tags)
    links = []     # (source_passage, target_string, file)

    for path in twee_files:
        text = path.read_text(encoding="utf-8")
        lines = text.split("\n")
        current_passage = None
        for line in lines:
            m = PASSAGE_HEADER_RE.match(line)
            if m and line.startswith("::"):
                name = m.group(1).strip()
                tags = set((m.group(2) or "").split())
                passages[name] = (path, tags)
                current_passage = name
                continue
            if current_passage:
                for link_match in LINK_RE.finditer(line):
                    target = parse_link_target(link_match.group(1))
                    links.append((current_passage, target, path))

    broken = []
    dynamic = []
    for source, target, path in links:
        if DYNAMIC_TARGET_RE.match(target):
            dynamic.append((source, target, path))
        elif target not in passages:
            broken.append((source, target, path))

    start = find_start_passage()
    if start not in passages:
        print(f"ERROR: start passage {start!r} (from StoryData) is not defined anywhere.")
        sys.exit(1)

    graph = {}
    for source, target, _ in links:
        if DYNAMIC_TARGET_RE.match(target):
            continue
        graph.setdefault(source, set()).add(target)

    reachable = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in reachable:
            continue
        reachable.add(node)
        stack.extend(graph.get(node, ()))

    orphans = [
        name for name, (path, tags) in passages.items()
        if name not in reachable
        and name not in SPECIAL_PASSAGE_NAMES
        and not (tags & SPECIAL_TAGS)
    ]

    ok = True

    if broken:
        ok = False
        print(f"BROKEN LINKS ({len(broken)}):")
        for source, target, path in broken:
            print(f"  {path.relative_to(Path(__file__).parent)}: {source!r} -> {target!r} (no such passage)")
        print()

    if dynamic:
        print(f"Dynamic links skipped, not statically checkable ({len(dynamic)}):")
        for source, target, path in dynamic:
            print(f"  {path.relative_to(Path(__file__).parent)}: {source!r} -> {target!r}")
        print()

    if orphans:
        print(f"UNREACHABLE from Start ({len(orphans)}) -- may be intentional:")
        for name in orphans:
            print(f"  {name!r} ({passages[name][0].relative_to(Path(__file__).parent)})")
        print()

    if ok and not orphans:
        print(f"OK: {len(passages)} passages, {len(links)} links, all reachable from {start!r}.")
    elif ok:
        print(f"OK: no broken links. {len(passages)} passages checked.")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
