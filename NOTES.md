# Decision log

Append-only. Each entry captures *why* a non-obvious choice was made, not
the current state of things (that's what the code and README are for).
Old entries aren't updated when superseded — the next entry is the
correction.

## 2026-08-23

**Tweego + SugarCube over the Twine desktop editor.** The editor stores a
whole story in one file, which doesn't work with multiple writers.
Tweego compiles a directory tree of plain `.twee` files into one HTML
build artifact instead — real files, real diffs, no single-file lock-in.

**Local toolchain isolation (`tools/`).** Tweego + the SugarCube
storyformat are fetched by `setup.sh`/`setup.ps1` into `tools/`
(gitignored), version-pinned in the scripts. Nothing installed globally,
so every contributor gets identical compiler/storyformat versions. Same
pattern later reused for Python (`spec/` venv, `pyproject.toml`).

**Marx's Ghost quote pool: full corpus + automatic extraction, not
hand-picked quotes.** Started with ~12 hand-verified quotes; scaling to
"a lot more" by hand didn't scale. Settled on: fetch the full public
domain text of *Capital* Vol. 1 (Python, stdlib only), commit it as
plain text (`story/shared/marx-corpus/capital-vol1.txt` — a big text
file is fine in git, it's exactly what git is good at), then
automatically extract quotable sentences by heuristic filters, no manual
review pass. Accepted tradeoff: occasional awkward/decontextualized
lines, in exchange for variety and zero ongoing curation cost.

**Corpus pipeline is decoupled in time from `build.sh`.** The Python
scripts (`fetch_and_clean.py`, `extract_quotes.py`) are run manually,
occasionally, and their *output* (`marx-quotes.txt`) is committed.
`build.sh`/`build.ps1` only ever read that committed file — they never
invoke Python. Nobody needs Python installed just to build or play the
game, only to update the quote corpus.

**Perl considered and rejected for the corpus pipeline**, despite being
already present (bundled with Git for Windows) and initially used for a
prototype. Rejected because introducing a language nobody else on the
project reads is a real cost, independent of whether it happens to
already be on `PATH`.

**Dramatis personae: name → link target, not hardcoded markup per
mention.** `<<character "Key">>` widget looks a key up in
`setup.characters` and renders either a local bio-passage link or an
external (Wikipedia) link, using SugarCube's own external-link detection
rather than branching by hand. Key is decoupled from display text so
"Fukuyama" can render as "Francis Fukuyama."

**`check_links.py`: deterministic static checks, stdlib Python, no
browser.** Built after confirming empirically that Tweego does *not*
validate that `[[link]]` targets exist — a real gap, not a redundant
tool. Deliberately scoped to graph-shape checks only (broken links,
passage reachability from Start); does not and can't catch runtime bugs
(e.g. a JS syntax error inside a `[script]` passage) — that still needs
the browser-driven checks below.

**No automated browser test framework adopted.** Playwright/Selenium
considered and set aside as too heavy for the project's current size.
Testing is currently manual: driving the compiled game's SugarCube API
directly in a browser (`Engine.play()`, `State.variables`, console/DOM
assertions) rather than clicking through the UI. If automated
browser-driven tests are wanted later, Playwright-via-Python was the
leading candidate (fits the existing venv, no Node needed) over
Selenium/Puppeteer.

**`refs/` and `var/`**: local-only, gitignored. `refs/` holds reference
material (e.g. SugarCube docs) for lookup during development; `var/` is
scratch output (logs, etc.) that stays inside the project instead of
leaking to `/tmp`.
