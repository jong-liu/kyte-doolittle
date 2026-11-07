# Kyte–Doolittle Hydropathy Scale — 專案藍圖

> 進度日誌：Obsidian `kyte–doolittle/kyte–doolittle/工作筆記.md`
> GitHub：https://github.com/jong-liu/kyte-doolittle
> Paper Reference: Kyte J., Doolittle R.F. J. Mol. Biol. 157:105-132(1982)

## 📌 專案目標

計算並可視化蛋白質序列的 Kyte–Doolittle hydropathy scale，預測跨膜螺旋（7-TM helices）
與親水/疏水域，用於蛋白質結構分析與藥物靶點評估。

## 🏗️ 架構概覽

| 階段 | 模組 | 用途 | 狀態 |
|---|---|---|---|
| 核心計算 | `src/kyte_doolittle.py` | Kyte-Doolittle scale（20 amino acids）+ 滑動窗口 | ⬜ |
| 序列輸入 | `src/utils.py` | FASTA/直接字串/UniProtKB AC 查詢 | ⬜ |
| 後端 API | `src/web_api.py` | FastAPI REST endpoint | ⬜ |
| 前端 | `frontend/` | HTML5 + Plotly.js 可視化 + 下載 CSV | ⬜ |
| 資料持久 | Firebase Realtime DB | 查詢結果、用戶計算歷史（7 日 TTL） | ⬜ |
| 部署 | GitHub Pages + Vercel/Render | Web 應用在線訪問 | ⬜ |

## ⚙️ 可調參數

```
1. Window size:            default=9;  odd numbers 3-21
2. Edge weight (%):        default=100; 0-100
3. Weight model:           "linear" or "exponential" (if <100)
4. Normalize (0-1):        yes/no (default: no)
```

## 📊 預期輸出

- **數值結果**：每個位置的 hydropathy score
- **圖表**：Plotly 交互式 line plot（position vs score）
- **特徵預測**：標記疏水高峰（可能的 TM helix）、邊界
- **下載**：CSV（位置 + score）、PNG/SVG 圖表

## 🛠️ 工具選型

| 工具 | 用途 | 版本 |
|---|---|---|
| Python | 核心 | 3.11+ |
| FastAPI | REST API | latest |
| Plotly | 可視化 | latest |
| Requests | UniProtKB API | latest |
| Pandas | 數據處理 | latest |
| Firebase Admin SDK | 資料存儲 | latest |
| React/Vue (optional) | 前端 UI | 最新 LTS |

## 📋 工作模式

- **加新工具/功能**：說「我想做一個 XXX」
- **結束對話**：說「收工」→ Obsidian 工作筆記 + git commit + push
- **接續工作**：說「開工」→ 讀工作筆記 + git 狀態 + 建議下一步

## 🪑🐙📘🔥 一桌三櫃

| 家 | 位置 | 用途 |
|---|---|---|
| 🪑 工作桌 | `G:\我的雲端硬碟\claude\projects\kyte–doolittle` | 代碼開發、即時編輯 |
| 🐙 GitHub | `jong-liu/kyte-doolittle` (public) | 版本管理、Pages 部署 |
| 📘 Obsidian | `vault/kyte–doolittle/kyte–doolittle/工作筆記.md` | 進度日誌、踩坑筆記 |
| 🔥 Firebase | `kyte-doolittle` project | 查詢結果存儲（7 日 TTL） |

## ⚠️ 鐵則

- `.claude/` 永不 commit（環境變數、API key 放這裡）
- Firebase key / UniProtKB token 絕不進 repo（`.env` + `.gitignore`）
- commit message 寫清楚「做了什麼 + 為什麼」
- 雲端 git 前設 `git config windows.appendAtomically false`

## 📝 開放問題 / Next Steps

- [ ] 核心計算實作 + 單元測試
- [ ] FastAPI endpoint 設計 + 測試
- [ ] 前端 UI 原型（簡單 HTML 或 React）
- [ ] UniProtKB API 集成（AC/ID 查詢）
- [ ] Firebase 資料結構設計 + TTL 規則
- [ ] 部署流程（GitHub Pages + API 服務）
- [ ] 論文附圖參考驗證（對標 Kyte-Doolittle 原論文結果）
