# Spectres

An adventure game built in Twine ([SugarCube](https://www.motoslave.net/sugarcube/2/) format), compiled from plain-text `.twee` files with [Tweego](https://www.motoslave.net/tweego/) — plain files instead of one editor blob, so multiple writers can work without clobbering each other.

## Setup

No global install — `tools/` is a version-pinned, gitignored local toolchain (Tweego + SugarCube), fetched by a setup script. Run once, and again whenever the pinned versions in the script change:

```bash
./setup.sh
```

Windows/PowerShell: `./setup.ps1`

## Build

```bash
./build.sh            # -> dist/index.html
./build.sh --watch    # rebuild on save
```

Windows/PowerShell: `./build.ps1` / `./build.ps1 -Watch`. Open `dist/index.html` in a browser to play.

## Conventions

- One area = one folder under `story/areas/`. Drop `.twee` files in freely — Tweego recurses the whole `story/` tree regardless of folder/file names.
- **Passage names must be unique across the whole tree** — the only real coordination cost between writers.
- Tag passages by area (see `tag-colors` in `story/config/00-story-data.twee`).
- `[stylesheet]`/`[script]`-tagged passages from anywhere are concatenated automatically, so an area can ship its own CSS/JS instead of piling into `config/`. `StoryInit` (default `$variables`) is a single shared passage, not a per-file tag.

For Twee/SugarCube syntax, see the [Tweego](https://www.motoslave.net/tweego/) and [SugarCube](https://www.motoslave.net/sugarcube/2/docs/) docs.
