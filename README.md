# 🧬 Kyte–Doolittle Hydropathy Scale Calculator

[English](#english) | [中文](#中文)

---

## 中文

Kyte–Doolittle hydropathy scale 是預測蛋白質疏水性域的經典方法，廣泛用於：
- 📍 預測跨膜螺旋（7-TM 結構）
- 🌊 分析蛋白質親疏水域
- 💊 藥物靶點評估

### 🚀 快速開始

```bash
# 1. 克隆或進入工作目錄
cd kyte-doolittle

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 運行核心計算
python -c "
from src.kyte_doolittle import calculate_hydropathy
seq = 'MVLSPADKTNVIRAAQNCYSTEIN...'  # 蛋白質序列
result = calculate_hydropathy(seq, window_size=9)
print(result)
"

# 4. 啟動 Web 應用
uvicorn src.web_api:app --reload
# 訪問 http://localhost:8000
```

### 📊 Web 界面

- 🔤 支持序列輸入：FASTA、直接字串、UniProtKB AC/ID
- 🎨 交互式 Plotly 圖表
- ⚙️ 可調參數：window size、邊界權重、正規化
- 💾 下載結果：CSV、PNG

### 📚 參數說明

| 參數 | 預設 | 範圍 | 說明 |
|---|---|---|---|
| `window_size` | 9 | 3-21（奇數） | 滑動窗口大小 |
| `edge_weight` | 100 | 0-100(%) | 窗口邊界相對權重 |
| `weight_model` | linear | linear/exponential | 邊界權重衰減模式 |
| `normalize` | False | True/False | 結果正規化 (0-1) |

### 🧪 測試

```bash
pytest tests/
```

### 📖 論文參考

> Kyte J., Doolittle R.F. 
> "A simple method for displaying the hydropathic character of a protein"
> *J. Mol. Biol.* 157:105-132 (1982)

---

## English

The Kyte–Doolittle hydropathy scale is a classic method for predicting protein hydrophobic regions, widely used for:
- 📍 Transmembrane helix prediction (7-TM structures)
- 🌊 Hydropathy profile analysis
- 💊 Drug target assessment

### 🚀 Quick Start

```bash
pip install -r requirements.txt
uvicorn src.web_api:app --reload
```

Visit `http://localhost:8000` for the web interface.

### 📦 Project Structure

```
kyte-doolittle/
├── src/
│   ├── kyte_doolittle.py      # Core calculation
│   ├── utils.py               # Sequence I/O, UniProtKB query
│   └── web_api.py             # FastAPI backend
├── frontend/                  # HTML/React UI
├── tests/                     # Unit tests
├── requirements.txt           # Dependencies
└── docs/                      # Documentation & references
```

---

## 🔗 Links

- **GitHub**: https://github.com/jong-liu/kyte-doolittle
- **Obsidian**: `kyte-doolittle/kyte–doolittle/工作筆記.md` (progress log)
- **Firebase**: Query results storage (7-day TTL)

---

**Last Updated**: 2026-11-07
