# 發佈與 LGPL 合規（DISTRIBUTION）

本文件供**維護者**在對外或對內散布 `nar_sat_dp` 執行檔時使用。

## 發佈物形式（方案 1）

**請勿只散布單一 `.exe`。** 正式發佈應為 zip，使用者解壓後目錄結構如下：

```text
NAR_SAT_DP_<版本>/
├── nar_sat_dp.exe          # 雙擊執行
├── README.txt              # 使用者簡短說明
├── LICENSE                 # Apache 2.0（本專案原始碼）
├── NOTICE                  # 第三方元件摘要
├── BUILD.md                # 建置與重現說明（方案 3）
├── config/                 # 執行期設定（可選調整）
│   └── pipeline.json
└── THIRD_PARTY/
    ├── LGPL-2.1.txt        # GNU LGPL 2.1 全文
    ├── py7zr-SOURCE.txt    # py7zr 原始碼取得方式與版本
    ├── py7zr-LICENSE.txt   # py7zr 授權摘要
    ├── openpyxl-LICENSE.txt # openpyxl MIT 授權（自套件複製）
    └── BUILD_VERSIONS.txt  # 建置時鎖定之套件版本
```

使用者**僅需解壓後雙擊 `nar_sat_dp.exe`**；其餘檔案為授權合規與重現建置用。

## 建置發佈包

```powershell
.\scripts\build.ps1
```

產出：

- `dist/NAR_SAT_DP_<版本>/` — 未壓縮發佈目錄
- `dist/NAR_SAT_DP_<版本>.zip` — 建議上傳/散布的檔案

## LGPL（py7zr）檢查清單

發佈 zip 前確認：

- [ ] `LICENSE`（Apache 2.0）已包含
- [ ] `NOTICE` 已包含
- [ ] `THIRD_PARTY/LGPL-2.1.txt` 全文已包含
- [ ] `THIRD_PARTY/py7zr-SOURCE.txt` 含版本號與原始碼 URL
- [ ] `THIRD_PARTY/BUILD_VERSIONS.txt` 含建置時 py7zr 等版本
- [ ] `BUILD.md` 說明如何自原始碼重建
- [ ] （建議）書面提供：三年內可索取對應 py7zr 原始碼之聯絡方式（見 `packaging/SOURCE_OFFER.txt`）

## 各元件授權摘要

| 元件 | 授權 | 發佈義務 |
|------|------|----------|
| NAR_SAT_DP 原始碼 | Apache 2.0 | 附 `LICENSE` |
| openpyxl（內嵌） | MIT | 附 `openpyxl-LICENSE.txt` |
| py7zr（內嵌） | LGPL-2.1+ | 附 LGPL 全文 + 原始碼取得說明 + 建置說明 |
| PyInstaller | GPL + exception | 僅建置期使用，不需隨 exe 散布 |

## 方案 3：為何附 BUILD.md

onefile exe 將 py7zr 內嵌於單檔，實務上較難單獨替換函式庫。附**可重現建置說明**可：

- 說明此發佈版如何產生
- 供進階使用者/法務稽核參考
- 方便維護者日後打出相同環境之建置

## 相關文件

- [BUILD.md](BUILD.md) — 建置步驟
- [NOTICE](../NOTICE) — 第三方聲明
- [NAR_SAT_DP_SDS.md](NAR_SAT_DP_SDS.md) §2.2 部署架構

---

本文件不構成法律意見；對外商用發佈前建議由法務審閱。
