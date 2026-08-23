#!/usr/bin/env pwsh
# Compiles story/ into a single playable HTML file at dist/index.html,
# using the project-local Tweego toolchain in tools/ (see setup.ps1).
#
# Usage:
#   ./build.ps1          # one-off build
#   ./build.ps1 -Watch   # rebuild on file save (does not re-run the data
#                          pipeline below if only *.txt sources change)

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

# Data pipeline: turn hand-authored plain-text sources into generated
# .twee passages (gitignored) before Tweego compiles the story. Each
# pipeline step reads a *.txt source and writes a *.gen.twee passage of
# the same name.

function New-JsonLinesPassage {
    param($Src, $Out, $PassageName)

    $quotes = Get-Content -Path $Src -Encoding utf8 |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ -and -not $_.StartsWith("#") }

    $json = @{ quotes = @($quotes) } | ConvertTo-Json -Compress

    Set-Content -Path $Out -Encoding utf8 -Value @(
        ":: $PassageName [data]"
        $json
    )
}

New-JsonLinesPassage -Src "story/shared/marx-quotes.txt" -Out "story/shared/marx-quotes.gen.twee" -PassageName "Marx Quotes"

New-Item -ItemType Directory -Force -Path dist | Out-Null

$tweegoArgs = @("-o", "dist/index.html", "story")
if ($Watch) {
    $tweegoArgs = @("-w") + $tweegoArgs
}

& $tweego @tweegoArgs
