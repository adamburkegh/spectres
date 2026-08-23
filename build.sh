#!/usr/bin/env bash
# Compiles story/ into a single playable HTML file at dist/index.html,
# using the project-local Tweego toolchain in tools/ (see setup.sh).
#
# Usage:
#   ./build.sh          # one-off build
#   ./build.sh --watch  # rebuild on file save
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

mkdir -p dist

if [[ "${1:-}" == "--watch" ]]; then
    "$tweego" -w -o dist/index.html story
else
    "$tweego" -o dist/index.html story
fi
