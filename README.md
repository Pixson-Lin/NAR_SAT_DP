# NAR_SAT_DP

批次讀取 GNSS 設備 log（`.txt`、`.zip`、`.7z`），解析衛星狀態後合併輸出為 **CSV + Excel**。

## 功能摘要

- 輸入：直接 `.txt`，或壓縮檔內所有 `.txt`
- 一台設備（一次 SSH）→ **2 列**（GPS、GLONASS）
- 輸出：同時產生 `.csv`（flat）與 `.xlsx`（含標題合併、部分欄位跨列合併）
- 交付：Python + PyInstaller 單一 exe（使用者無需安裝 Python / 7-Zip）

完整規格見 [docs/DECISIONS.md](docs/DECISIONS.md)、[docs/NAR_SAT_DP_SRS.md](docs/NAR_SAT_DP_SRS.md)（需求）、[docs/NAR_SAT_DP_SDS.md](docs/NAR_SAT_DP_SDS.md)（設計）。

## 快速開始（開發模式）

```powershell
cd C:\Users\Pixson\Documents\Projects\NAR_SAT_DP
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e . -r requirements-dev.txt
```

### 解析與批次轉檔

```powershell
# 單一 .7z、.zip、.txt 或整個資料夾
python -m nar_sat_dp "references/samples/tools dump VBS log.7z" -o "references/samples/_output"

# 多個輸入合併
python -m nar_sat_dp references/samples/new` 7.txt references/samples/new` 8.txt -o merged
```

未指定 `-o` 時，預設在同目錄產出 `merged.csv` / `merged.xlsx`。

執行時會顯示進度；結束時印出摘要。若有錯誤會寫入 `<輸出檔名>_errors.log`。

亦可使用預覽腳本（行為與主程式相同）：

```powershell
python scripts/parse_gnss_preview.py "references/samples/new 7.txt" -o references/samples/_preview
```

## 輸入 log 結構

每台 NE 的 `.txt` 為一次 SSH session，核心指令如下（`environment no more`、`logout` 忽略）：

| 指令 | 用途 |
|------|------|
| `tools dump port a/gnss gnss` | 控制卡 A 衛星表 |
| `tools dump port b/gnss gnss` | 控制卡 B 衛星表 |
| `show port a/gnss \| match "Angle     :"` | 控制卡 A 仰角遮罩 |
| `show port b/gnss \| match "Angle     :"` | 控制卡 B 仰角遮罩 |

正式 log 在**第一個 hostname 出現前**可能有 `[BEGIN] {timestamp}` 行，會擷取為 `script_begin_time`。

範例檔：`references/samples/`（含 `new 7.txt`、`new 8.txt` 與正式版 log）。

## 輸出欄位（欄位順序）

| 區段 | 欄位 |
|------|------|
| 識別 | hostname, Control, Elev. Mask Angle, Used Satellite(Control), Constellation, Used Satellite(Constellation) |
| 訊號 | A signal 1…16, B signal 1…16 |
| 時間 | script_begin_time |
| 追溯（批次時） | source_archive, source_txt_path |

- **A / B**：控制卡 A / B（非「port」泛稱）
- **分列**：GPS 列 + GLONASS 列；其他 Constellation 略過
- **訊號不足 16**：以 `-` 補位
- **Used Satellite(Control)**：各控制卡 dump 結尾 `No. of Used Satellites`
- **Used Satellite(Constellation)**：格式 `{總數}({卡A數}+{卡B數})`，例如 `18(9+9)`

## CSV vs Excel

| 項目 | CSV | Excel |
|------|-----|-------|
| 欄位 | 同上順序，flat | 雙層標題（A/B signal 區塊合併） |
| hostname | 每列重複 | 同一 NE 的 GPS/GLONASS **合併** |
| Elev. Mask Angle | 每列各自填值 | **不合併**（每列獨立儲存格） |
| script_begin_time | 每列重複 | 同一 NE **合併** |
| source_* | 每列重複 | 同一 NE **合併** |

## 批次用法

```text
nar_sat_dp.exe <輸入路徑...> -o <輸出基底名稱> [-c pipeline.json]
```

- 可傳入多個資料夾、`.txt`、`.zip`、`.7z`；資料夾會遞迴掃描
- **拖放**：將檔案或資料夾拖到 `nar_sat_dp.exe` 上（預設輸出 `merged.csv` / `merged.xlsx`）
- 同時產出 `.csv` 與 `.xlsx`；錯誤寫入 `<輸出檔名>_errors.log`
- 結束碼：0 成功、1 有警告仍產出、2 失敗

## 設定檔

| 檔案 | 說明 |
|------|------|
| [config/pipeline.json](config/pipeline.json) | 掃描、編碼、錯誤處理 |
| [config/fields.json](config/fields.json) | 舊版 placeholder 規則（GNSS 解析已改為程式內建） |

## 打包與發佈

```powershell
pip install -r requirements-dev.txt
.\scripts\build.ps1
```

產出：

| 路徑 | 說明 |
|------|------|
| `dist/nar_sat_dp.exe` | 單一執行檔 |
| `dist/NAR_SAT_DP_<版本>/` | 發佈目錄（exe + 授權 + `THIRD_PARTY/` + `BUILD.md`） |
| `dist/NAR_SAT_DP_<版本>.zip` | **建議散布給使用者**（解壓後雙擊 exe） |

發佈與 LGPL 合規說明見 [docs/DISTRIBUTION.md](docs/DISTRIBUTION.md)、建置重現見 [docs/BUILD.md](docs/BUILD.md)。

## 授權

本專案原始碼以 [Apache License 2.0](LICENSE) 授權。

第三方套件授權見 [NOTICE](NOTICE)。**請以 zip 發佈包**（含 `THIRD_PARTY/` 與 `BUILD.md`）散布 exe，以符合內嵌 py7zr（LGPL-2.1+）之義務。

## 結束碼

| 碼 | 意義 |
|----|------|
| 0 | 全部成功 |
| 1 | 有警告/錯誤但已產出檔案 |
| 2 | 無法產出輸出 |
