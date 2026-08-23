#!/usr/bin/env bash
# Sets up an isolated, version-pinned toolchain in tools/ — this project's
# equivalent of a venv. Nothing gets installed globally; tools/ is gitignored
# and every contributor runs this once (and again whenever the pinned
# versions below change) to get the same Tweego + SugarCube versions.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

TWEEGO_VERSION="2.1.1"
SUGARCUBE_VERSION="2.37.3"

case "$(uname -s)" in
    Linux*)   os="linux" ;;
    Darwin*)  os="macos" ;;
    MINGW*|MSYS*|CYGWIN*) os="windows" ;;
    *) echo "Unsupported OS: $(uname -s)" >&2; exit 1 ;;
esac

case "$(uname -m)" in
    x86_64|amd64) arch="x64" ;;
    i386|i686)    arch="x86" ;;
    *) echo "Unsupported architecture: $(uname -m)" >&2; exit 1 ;;
esac

tweego_asset="tweego-${TWEEGO_VERSION}-${os}-${arch}.zip"
tweego_url="https://github.com/tmedwards/tweego/releases/download/v${TWEEGO_VERSION}/${tweego_asset}"
sugarcube_url="https://github.com/tmedwards/sugarcube-2/releases/download/v${SUGARCUBE_VERSION}/sugarcube-${SUGARCUBE_VERSION}-for-twine-2.1-local.zip"

rm -rf tools/tweego tools/_dl
mkdir -p tools/_dl

echo "Downloading Tweego ${TWEEGO_VERSION} (${os}/${arch})..."
curl -sL -o tools/_dl/tweego.zip "$tweego_url"

echo "Downloading SugarCube ${SUGARCUBE_VERSION}..."
curl -sL -o tools/_dl/sugarcube.zip "$sugarcube_url"

unzip -q tools/_dl/tweego.zip -d tools/tweego
# Overlay the pinned SugarCube version over whatever Tweego bundled, since
# Tweego releases ship whatever storyformat snapshot was current at the time.
unzip -oq tools/_dl/sugarcube.zip -d tools/tweego/storyformats

rm -rf tools/_dl

if [[ "$os" == "windows" ]]; then
    bin="tools/tweego/tweego.exe"
else
    bin="tools/tweego/tweego"
    chmod +x "$bin"
fi

echo
"$bin" --version
echo
echo "Done. Toolchain installed in tools/ (gitignored). Run ./build.sh to compile the story."
