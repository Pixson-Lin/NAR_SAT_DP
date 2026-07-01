# 於專案根目錄執行，產出 dist/nar_sat_dp.exe
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "建議先建立 venv 並 pip install -r requirements-dev.txt"
}

python -m PyInstaller `
    --onefile `
    --name nar_sat_dp `
    --paths src `
    --hidden-import py7zr `
    --collect-submodules py7zr `
    --add-data "config;config" `
    src/nar_sat_dp/__main__.py

Write-Host "完成: dist\nar_sat_dp.exe"
