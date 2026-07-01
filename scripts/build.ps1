# 於專案根目錄執行：建置 exe 並組裝 LGPL/Apache 合規發佈 zip（方案 1 + 3）
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $Python = "python"
    Write-Host "未偵測到 .venv，使用系統 python"
}

$Version = & $Python -c "import sys; sys.path.insert(0, 'src'); from nar_sat_dp import __version__; print(__version__)"
$ReleaseName = "NAR_SAT_DP_$Version"
$ReleaseDir = Join-Path $Root "dist\$ReleaseName"
$ZipPath = Join-Path $Root "dist\$ReleaseName.zip"

Write-Host "版本: $Version"
Write-Host "建置 exe..."

& $Python -m PyInstaller `
    --noconfirm `
    --onefile `
    --name nar_sat_dp `
    --paths src `
    --hidden-import py7zr `
    --collect-submodules py7zr `
    --hidden-import openpyxl `
    --collect-submodules openpyxl `
    --add-data "config;config" `
    src/nar_sat_dp/__main__.py

$ExePath = Join-Path $Root "dist\nar_sat_dp.exe"
if (-not (Test-Path $ExePath)) {
    throw "找不到 dist\nar_sat_dp.exe"
}

Write-Host "組裝發佈目錄: $ReleaseDir"
if (Test-Path $ReleaseDir) {
    Remove-Item $ReleaseDir -Recurse -Force
}
New-Item -ItemType Directory -Path $ReleaseDir | Out-Null

$ThirdParty = Join-Path $ReleaseDir "THIRD_PARTY"
New-Item -ItemType Directory -Path $ThirdParty | Out-Null

Copy-Item $ExePath (Join-Path $ReleaseDir "nar_sat_dp.exe")
Copy-Item (Join-Path $Root "LICENSE") $ReleaseDir
Copy-Item (Join-Path $Root "NOTICE") $ReleaseDir
Copy-Item (Join-Path $Root "docs\BUILD.md") $ReleaseDir
Copy-Item (Join-Path $Root "packaging\RELEASE_README.txt") (Join-Path $ReleaseDir "README.txt")
Copy-Item (Join-Path $Root "packaging\licenses\LGPL-2.1.txt") $ThirdParty
Copy-Item (Join-Path $Root "packaging\SOURCE_OFFER.txt") (Join-Path $ThirdParty "py7zr-SOURCE.txt")
Copy-Item (Join-Path $Root "config") (Join-Path $ReleaseDir "config") -Recurse

& $Python (Join-Path $Root "scripts\write_release_metadata.py") $ThirdParty

Write-Host "壓縮: $ZipPath"
if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}
Compress-Archive -Path $ReleaseDir -DestinationPath $ZipPath

Write-Host ""
Write-Host "完成:"
Write-Host "  exe:      dist\nar_sat_dp.exe"
Write-Host "  發佈目錄: dist\$ReleaseName\"
Write-Host "  發佈 zip: dist\$ReleaseName.zip"
Write-Host ""
Write-Host "使用者：解壓 zip 後雙擊 nar_sat_dp.exe 即可執行。"
