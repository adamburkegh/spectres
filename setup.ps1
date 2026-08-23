#!/usr/bin/env pwsh
# Sets up an isolated, version-pinned toolchain in tools/ -- this project's
# equivalent of a venv. Nothing gets installed globally; tools/ is gitignored
# and every contributor runs this once (and again whenever the pinned
# versions below change) to get the same Tweego + SugarCube versions.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$TweegoVersion = "2.1.1"
$SugarCubeVersion = "2.37.3"

$arch = if ([Environment]::Is64BitOperatingSystem) { "x64" } else { "x86" }

$tweegoAsset = "tweego-$TweegoVersion-windows-$arch.zip"
$tweegoUrl = "https://github.com/tmedwards/tweego/releases/download/v$TweegoVersion/$tweegoAsset"
$sugarcubeUrl = "https://github.com/tmedwards/sugarcube-2/releases/download/v$SugarCubeVersion/sugarcube-$SugarCubeVersion-for-twine-2.1-local.zip"

Remove-Item -Recurse -Force -ErrorAction SilentlyContinue tools/tweego, tools/_dl
New-Item -ItemType Directory -Force -Path tools/_dl | Out-Null

Write-Host "Downloading Tweego $TweegoVersion (windows/$arch)..."
Invoke-WebRequest -Uri $tweegoUrl -OutFile tools/_dl/tweego.zip

Write-Host "Downloading SugarCube $SugarCubeVersion..."
Invoke-WebRequest -Uri $sugarcubeUrl -OutFile tools/_dl/sugarcube.zip

Expand-Archive -Path tools/_dl/tweego.zip -DestinationPath tools/tweego -Force
# Overlay the pinned SugarCube version over whatever Tweego bundled, since
# Tweego releases ship whatever storyformat snapshot was current at the time.
Expand-Archive -Path tools/_dl/sugarcube.zip -DestinationPath tools/tweego/storyformats -Force

Remove-Item -Recurse -Force tools/_dl

Write-Host ""
& tools/tweego/tweego.exe --version
Write-Host ""
Write-Host "Done. Toolchain installed in tools/ (gitignored). Run ./build.ps1 to compile the story."
