# NAR_SAT_DP 決策與規格紀錄

本文件記錄已拍板的跨格式決策與 GNSS 解析規格。變更時請同步更新本文件與 `README.md`。

## 已確認約束

| 項目 | 決策 |
|------|------|
| 外部依賴 | 完全零外部依賴（使用者端不需安裝 Python、7-Zip、pip 套件等） |
| 輸入 | `.txt` 直接檔，或 `.zip` / `.7z` 內所有 `.txt` |
| 輸出格式 | **雙輸出**：`.csv`（flat）+ `.xlsx`（openpyxl，含標題與部分欄位合併） |
| 技術選型 | Python + PyInstaller（開發期可用 pip；交付為單一 exe） |
| 訊號欄位上限 | 每控制卡、每 Constellation 最多 **16** 筆，不足以 `-` 補位 |

---

## 1. 資料列（row）語意

| 問題 | 決策 |
|------|------|
| 一個 `.txt` 對應幾列？ | **1 次 SSH = 1 台 NE → 2 列 CSV/Excel 列** |
| 分列規則 | `tools dump` 表格依 **Constellation** 分塊：**GPS → 第 1 列、GLONASS → 第 2 列** |
| 其他 Constellation | **略過**（僅處理 GPS、GLONASS） |
| A / B 語意 | **控制卡 A / B**（對應 `port a` / `port b` 指令） |

---

## 1b. 輸入 log 結構（每台 NE）

單一 `.txt` 含一次 SSH session。核心為 6 道指令（①⑥忽略）：

| 指令 | 用途 |
|------|------|
| `environment no more` | 忽略 |
| `tools dump port a/gnss gnss` | 控制卡 A 衛星表（GPS / GLONASS 連續分塊） |
| `tools dump port b/gnss gnss` | 控制卡 B 衛星表 |
| `show port a/gnss \| match "Angle     :"` | 控制卡 A `Elev. Mask Angle` |
| `show port b/gnss \| match "Angle     :"` | 控制卡 B `Elev. Mask Angle` |
| `logout` | 忽略 |

### 正式 log 時間戳

- 在**第一個 hostname（`A:...#`）出現之前**，可能有 `[BEGIN] {timestamp}` 行（不一定在第 1 行）
- 擷取 `[BEGIN]` 後字串為 **`script_begin_time`**
- 同一 NE 的 GPS / GLONASS 兩列填相同值

範例檔：`references/samples/`。

---

## 1c. 輸出欄位（每台 NE × 2 列）

### 欄位順序

1. `hostname`
2. `Control`
3. `Elev. Mask Angle`
4. `Used Satellite(Control)`
5. `Constellation`
6. `Used Satellite(Constellation)`
7. `A signal 1` … `A signal 16`
8. `B signal 1` … `B signal 16`
9. `script_begin_time`
10. `source_archive`（批次時）
11. `source_txt_path`（批次時）

追溯欄位 **`source_archive`、`source_txt_path` 置於最後**（`script_begin_time` 之後）。

### 各欄擷取規則

| 欄位 | 規則 |
|------|------|
| hostname | prompt `A:{hostname}#` |
| Control | GPS 列 = `A`、GLONASS 列 = `B` |
| Elev. Mask Angle | GPS 列 = 控制卡 A `show port a`；GLONASS 列 = 控制卡 B `show port b` |
| Used Satellite(Control) | 控制卡 dump 結尾 `No. of Used Satellites: N`；GPS 列 = 卡 A、GLONASS 列 = 卡 B |
| Constellation | `GPS` 或 `GLONASS` |
| Used Satellite(Constellation) | `{卡A該系統數+卡B該系統數}({卡A數}+{卡B數})`，例：`20(10+10)`、`10(6+4)` |
| A signal 1…16 | 控制卡 A、該 Constellation 各資料列最後一欄（C/No）；>16 取前 16 |
| B signal 1…16 | 控制卡 B 同上 |
| script_begin_time | `[BEGIN]` 時間字串 |

### `new 7.txt` 參考輸出

| 欄位 | GPS 列 | GLONASS 列 |
|------|--------|------------|
| hostname | 7250-IXR-R6_Down | 7250-IXR-R6_Down |
| Control | A | B |
| Elev. Mask Angle | 15 | 15 |
| Used Satellite(Control) | 16 | 14 |
| Constellation | GPS | GLONASS |
| Used Satellite(Constellation) | 20(10+10) | 10(6+4) |
| A signal（有效） | 10 筆 GPS 訊號 | 6 筆 GLONASS 訊號 |
| B signal（有效） | 10 筆 GPS 訊號 | 4 筆 GLONASS 訊號 |

---

## 1d. CSV vs Excel 版面

| 欄位 | CSV | Excel（同一 NE 的 GPS/GLONASS 兩列） |
|------|-----|--------------------------------------|
| hostname | 每列重複 | **合併** |
| Elev. Mask Angle | 每列填值 | **不合併**（各列獨立儲存格） |
| script_begin_time | 每列重複 | **合併** |
| source_archive / source_txt_path | 每列重複 | **合併** |
| A signal / B signal 標題 | 單層欄名 | 第 1 列區塊標題合併，第 2 列為 1…16 |

---

## 2. 批次輸入操作方式

| 問題 | 決策 |
|------|------|
| 啟動方式 | **CLI 參數** + **拖放到 exe** |
| 遞迴掃描 | **是** |
| 檔名篩選 | 預設 `*.txt`；壓縮檔 `*.zip`、`.7z` |
| 輸入路徑 | 可混合多資料夾、壓縮檔、獨立 txt |

---

## 3. 字元編碼

| 問題 | 決策 |
|------|------|
| 輸入編碼 | 自動偵測：UTF-8 BOM → UTF-8 → CP950 |
| 解碼失敗 | 跳過該檔，寫入錯誤 log |
| 輸出 CSV 編碼 | UTF-8 with BOM |

---

## 4. 輸出規格

| 問題 | 決策 |
|------|------|
| 格式 | CSV + XLSX 雙輸出 |
| CSV 分隔符 | 逗號，標準引號規則 |
| 訊號缺漏 | 填 `-` |
| 重複列 | 允許，不去重 |

---

## 5. 錯誤處理

| 問題 | 決策 |
|------|------|
| 部分失敗 | 繼續處理 |
| 產出物 | 主輸出 + `<輸出檔名>_errors.log` |
| 結束碼 | 0 成功；1 有警告仍產出；2 無法產出 |

---

## 6. `.7z` 策略

開發期 `py7zr`，PyInstaller 打包進 exe；7z 解至暫存目錄，zip 記憶體內讀取。

---

## 7. 實作模組

| 模組 | 用途 |
|------|------|
| `src/nar_sat_dp/gnss_parser.py` | GNSS log 解析 |
| `src/nar_sat_dp/gnss_output.py` | CSV + Excel 輸出 |
| `scripts/parse_gnss_preview.py` | 單檔/多檔預覽腳本 |

主批次 pipeline（`nar_sat_dp.cli`）尚待整合 GNSS 解析器與雙輸出。

---

## 8. 交付與維護

| 項目 | 決策 |
|------|------|
| 版本號 | `--version` |
| 說明文件 | `README.md` + [DECISIONS.md](DECISIONS.md) + [NAR_SAT_DP_SRS.md](NAR_SAT_DP_SRS.md) + [NAR_SAT_DP_SDS.md](NAR_SAT_DP_SDS.md) |
