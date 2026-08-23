# Spectres

An adventure game built in Twine, using the [SugarCube](https://www.motoslave.net/sugarcube/2/) story format and compiled from plain-text source files with [Tweego](https://www.motoslave.net/tweego/).

## Why this setup

The Twine editor stores a whole story in one `.html`/`.tws` file, which is unworkable with multiple writers. Tweego instead compiles a **directory tree of plain `.twee` text files** into one playable HTML file. That gives us:

- one file per passage or small group of passages, so different writers can work in different files without merge conflicts,
- normal git diffs/blame/PRs on story content,
- a build step, so the "compiled game" (`dist/index.html`) is just an artifact, not the source of truth.

The story format is SugarCube — mature, scriptable (JavaScript-backed macros/widgets), and it compiles to plain HTML/CSS/JS. That last part matters: once the base game is solid, there's nothing stopping later passages from reaching for canvas, CSS animations, the Web Audio API, `localStorage`, or a service worker, because the output *is* a web page.

## Setup

There's no global install. `tools/` is this project's equivalent of a venv: a version-pinned, project-local copy of Tweego + the SugarCube storyformat, fetched by a setup script and gitignored. Nothing touches your system `PATH`, and every contributor ends up with the exact same compiler/storyformat versions (pinned in `setup.sh`/`setup.ps1`).

```bash
./setup.sh
```

On Windows/PowerShell:

```powershell
./setup.ps1
```

Re-run it whenever the pinned versions in the script change. Safe to run again any time — it wipes and re-fetches `tools/tweego/`.

## Building

```bash
./build.sh          # one-off build -> dist/index.html
./build.sh --watch   # rebuild whenever a story file changes
```

On Windows/PowerShell:

```powershell
./build.ps1
./build.ps1 -Watch
```

Open `dist/index.html` in a browser to play. Both scripts fail fast with a reminder to run setup if `tools/` isn't there yet.

## Project layout

- `story/config/`
  - [00-story-data.twee](story/config/00-story-data.twee) — StoryData (IFID, format, start passage, tag-colors)
  - [01-story-title.twee](story/config/01-story-title.twee) — StoryTitle
  - [02-stylesheet.twee](story/config/02-stylesheet.twee) — global CSS (`[stylesheet]` passage)
  - [03-javascript.twee](story/config/03-javascript.twee) — global startup JS (`[script]` passage)
  - [04-story-init.twee](story/config/04-story-init.twee) — StoryInit, default `$variables`, runs before the first passage
- `story/shared/`
  - [widgets.twee](story/shared/widgets.twee) — reusable `<<widget>>` macros, available to every area
- `story/areas/castle/` — the only area so far
  - [gates.twee](story/areas/castle/gates.twee) — The Gates of Elsinore, current start passage
  - [courtyard.twee](story/areas/castle/courtyard.twee) — Castle Courtyard

Each area gets its own folder under `story/areas/` (`castle/` is the only one so far). When starting a new area, make a new folder and start dropping `.twee` files in it — Tweego doesn't care about folder or file names, only about passage names (the `:: Name` header inside each file) being unique across the whole tree.

### Passage file format

```
:: Passage Name [optional-tag]
Passage body text, [[links->Other Passage]], and <<macros>> go here.
```

- **Passage names must be unique across the entire `story/` tree** — that's the only real coordination cost between writers. Pick specific names (`Tavern Back Room`, not `Room`).
- One passage per file is fine for anything with meaningful content; small connector/transition passages can share a file if they belong to the same scene.
- Tag passages with their area (e.g. `[castle]`) — see `tag-colors` in [00-story-data.twee](story/config/00-story-data.twee) — so they're visually grouped if anyone opens the compiled story in the Twine editor for debugging.
- `[stylesheet]`- and `[script]`-tagged passages are all concatenated by SugarCube, so an area can ship its own CSS/JS alongside its passages instead of piling everything into `config/`.

### Adding a new writer's area

1. `mkdir story/areas/<area-name>`
2. Add `.twee` files there, one passage (or small scene) per file.
3. Link into it from an existing passage (e.g. from [The Gates of Elsinore](story/areas/castle/gates.twee) or another hub passage) with `[[Link text->Passage Name]]`.
4. `./build.sh` and open `dist/index.html` to check it.

## Later web-platform ideas

Because the compiled output is a normal web page, these are all in-reach without leaving Twine/SugarCube:
- ambient audio via the Web Audio API, triggered from `[script]` passages or widgets,
- CSS animations/transitions on passage transitions (SugarCube supports custom transition classes),
- a `[stylesheet]` passage per area for a distinct visual identity per location,
- extra persistent state via `localStorage` alongside SugarCube's own save system,
- eventually, hosting `dist/index.html` as a static site with no server needed.
