#!/usr/bin/env pwsh
# Compiles story/ into a single playable HTML file at dist/index.html,
# using the project-local Tweego toolchain in tools/ (see setup.ps1).
#
# Usage:
#   ./build.ps1          # one-off build
#   ./build.ps1 -Watch   # rebuild on file save

param(
    [switch]$Watch
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$tweego = "tools/tweego/tweego.exe"
if (-not (Test-Path $tweego)) {
    Write-Error "Local toolchain not found. Run ./setup.ps1 first."
    exit 1
}

New-Item -ItemType Directory -Force -Path dist | Out-Null

$tweegoArgs = @("-o", "dist/index.html", "story")
if ($Watch) {
    $tweegoArgs = @("-w") + $tweegoArgs
}

& $tweego @tweegoArgs
