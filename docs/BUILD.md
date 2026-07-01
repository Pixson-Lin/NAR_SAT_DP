# 建置與重現說明（BUILD）

本文件說明如何從原始碼建置 `nar_sat_dp.exe` 與正式發佈 zip。  
發佈包內會附本文件副本，供 LGPL 合規與日後重現建置參考。

## 環境需求

| 項目 | 版本 |
|------|------|
| 作業系統 | Windows 10 或以上 |
| Python | 3.10 或以上 |
| Git | 建議（取得原始碼） |

## 1. 取得原始碼

```powershell
git clone https://github.com/Pixson-Lin/NAR_SAT_DP.git
cd NAR_SAT_DP
```

或解開與本發佈對應之原始碼封存。

## 2. 建立虛擬環境並安裝依賴

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements-dev.txt
```

`requirements-dev.txt` 建置相關套件（建議鎖定版本後記錄於發佈說明）：

- `py7zr` — LGPL-2.1+，`.7z` 解壓（會被打包進 exe）
- `pyinstaller` — 建置工具
- `openpyxl` — MIT，Excel 輸出（會被打包進 exe）

建置前請記錄實際安裝版本（發佈腳本會自動寫入 `THIRD_PARTY/BUILD_VERSIONS.txt`）：

```powershell
pip freeze | Select-String "py7zr|pyinstaller|openpyxl"
```

## 3. 建置 exe 與發佈 zip

```powershell
.\scripts\build.ps1
```

腳本會：

1. 以 PyInstaller `--onefile` 產出 `dist/nar_sat_dp.exe`
2. 組裝 `dist/NAR_SAT_DP_<版本>/` 發佈目錄（含授權與 `THIRD_PARTY/`）
3. 壓縮為 `dist/NAR_SAT_DP_<版本>.zip`

## 4. PyInstaller 參數（與 build.ps1 一致）

使用 `scripts/pyi_entry.py`（絕對 import，避免 frozen exe 啟動失敗）：

```text
python -m PyInstaller ^
  --onefile ^
  --name nar_sat_dp ^
  --paths src ^
  --hidden-import py7zr ^
  --collect-submodules py7zr ^
  --add-data "config;config" ^
  scripts/pyi_entry.py
```

## 5. 驗證

```powershell
.\dist\NAR_SAT_DP_0.1.0\nar_sat_dp.exe --version
.\dist\NAR_SAT_DP_0.1.0\nar_sat_dp.exe references\samples\new` 7.txt -o test_out
```

（若主 CLI 尚未整合 GNSS，可改用 `scripts/parse_gnss_preview.py` 驗證解析邏輯。）

## 6. 與 LGPL（py7zr）相關說明

本 exe 以 onefile 方式內嵌 `py7zr`。若您要行使 LGPL 所賦予之替換函式庫權利，可：

1. 依本文件自原始碼重建 exe；或
2. 參考發佈包內 `THIRD_PARTY/py7zr-SOURCE.txt` 取得與發佈版對應之 py7zr 原始碼。

詳見 [DISTRIBUTION.md](DISTRIBUTION.md)。

---

文件版本：0.1.0
