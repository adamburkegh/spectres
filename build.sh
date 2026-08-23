#!/usr/bin/env bash
# Compiles story/ into a single playable HTML file at dist/index.html,
# using the project-local Tweego toolchain in tools/ (see setup.sh).
#
# Usage:
#   ./build.sh          # one-off build
#   ./build.sh --watch  # rebuild on file save (does not re-run the data
#                          pipeline below if only *.txt sources change)
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

if [[ -x "tools/tweego/tweego.exe" ]]; then
    tweego="tools/tweego/tweego.exe"
elif [[ -x "tools/tweego/tweego" ]]; then
    tweego="tools/tweego/tweego"
else
    echo "Local toolchain not found. Run ./setup.sh first." >&2
    exit 1
fi

# Data pipeline: turn hand-authored plain-text sources into generated
# .twee passages (gitignored) before Tweego compiles the story. Each
# pipeline step reads a *.txt source and writes a *.gen.twee passage of
# the same name.

gen_json_lines_passage() {
    local src="$1" out="$2" passage_name="$3"
    local quotes=() line

    while IFS= read -r line || [[ -n "$line" ]]; do
        line="${line%$'\r'}"
        [[ -z "$line" || "$line" == \#* ]] && continue
        line="${line//\\/\\\\}"   # escape backslashes
        line="${line//\"/\\\"}"   # escape double quotes
        quotes+=("\"$line\"")
    done < "$src"

    {
        printf ':: %s [data]\n' "$passage_name"
        printf '{"quotes": [%s]}\n' "$(IFS=,; echo "${quotes[*]}")"
    } > "$out"
}

gen_json_lines_passage story/shared/marx-quotes.txt story/shared/marx-quotes.gen.twee "Marx Quotes"

mkdir -p dist

if [[ "${1:-}" == "--watch" ]]; then
    "$tweego" -w -o dist/index.html story
else
    "$tweego" -o dist/index.html story
fi
