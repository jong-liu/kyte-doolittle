# 快速開始指南 (Getting Started)

## 🚀 5 分鐘快速開始

### 1. **安裝依賴**

```bash
pip install -r requirements.txt
```

### 2. **啟動應用**

#### **Windows 用戶**
```bash
run.bat
```
雙擊 `run.bat` 文件，或在命令行執行上述指令。

#### **macOS / Linux 用戶**
```bash
bash run.sh
```

### 3. **訪問應用**

- 🎨 **前端 UI**：http://localhost:8080
- 📡 **API 文檔**：http://localhost:8000/docs
- ✅ **健康檢查**：http://localhost:8000/api/health

---

## 📖 使用指南

### **輸入序列格式**

應用支持三種輸入格式：

#### 1️⃣ **FASTA 格式**
```
>sp|P12345|ABC_HUMAN
MVLSPADKTNVIRAAQNCYSTEIN
NQGNRG
```

#### 2️⃣ **UniProtKB Accession (AC)**
```
P12345
```
應用會自動從 UniProtKB 查詢完整序列。

#### 3️⃣ **UniProtKB ID**
```
TP53_HUMAN
```

#### 4️⃣ **原始序列**
```
MVLSPADKTNVIRAAQNCYSTEIN
```

---

### **參數說明**

| 參數 | 預設 | 範圍 | 說明 |
|---|---|---|---|
| **Window Size** | 9 | 3–21 (奇數) | 滑動窗口大小。越小越靈敏，越大越平滑。 |
| **Edge Weight (%)** | 100 | 0–100 | 窗口邊界相對權重。100% = 均勻權重，<100% = 邊界權重降低。 |
| **Weight Model** | linear | linear / exponential | 邊界權重衰減方式。linear = 線性，exponential = 指數。 |
| **Normalize** | ✗ | ✓/✗ | 是否將結果正規化至 0–1 範圍。 |
| **Query UniProtKB** | ✓ | ✓/✗ | 若輸入為 AC/ID，是否查詢 UniProtKB。 |

---

### **理解結果**

#### **圖表**
- **X 軸**：蛋白質序列位置（amino acid position）
- **Y 軸**：疏水性指數（hydropathy score）
  - **正值 (> 0)**：疏水性，傾向跨膜區域
  - **負值 (< 0)**：親水性，傾向溶液暴露區域

#### **統計資訊**
- **序列長度**：輸入序列包含的氨基酸數
- **最小/最大值**：疏水性指數的範圍
- **平均值**：全序列平均疏水性
- **標準差**：疏水性波動程度

---

## 🛠️ 手動運行各組件

### **只啟動後端 API**

```bash
python -m uvicorn src.web_api:app --reload
```

訪問 http://localhost:8000/docs 查看 API 文檔。

### **只啟動前端**

```bash
cd frontend
python -m http.server 8080
# 訪問 http://localhost:8080
```

### **運行測試**

```bash
pytest tests/test_kyte_doolittle.py -v
```

---

## 🧪 測試 API

### **使用 curl**

```bash
curl -X POST http://localhost:8000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "sequence": "MVLSPADKTNVIRAAQNCYSTEIN",
    "window_size": 9,
    "edge_weight": 100,
    "weight_model": "linear",
    "normalize": false,
    "query_uniprot": false
  }'
```

### **使用 Python**

```python
import requests

response = requests.post("http://localhost:8000/api/calculate", json={
    "sequence": "MVLSPADKTNVIRAAQNCYSTEIN",
    "window_size": 9,
    "edge_weight": 100,
    "weight_model": "linear",
    "normalize": False,
    "query_uniprot": False
})

result = response.json()
print(f"Scores: {result['scores']}")
print(f"Statistics: {result['metadata']}")
```

---

## 🚀 部署

### **部署到 Vercel（前端 + API）**

1. **推送到 GitHub**
   ```bash
   git push origin master
   ```

2. **在 Vercel 建立 Project**
   - 導入 `jong-liu/kyte-doolittle` repo
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn src.web_api:app --host 0.0.0.0`

3. **前端靜態部署**
   - 將 `frontend/index.html` 部署到 GitHub Pages 或 Vercel

### **部署到自託管伺服器**

1. **SSH 進入伺服器**
   ```bash
   ssh user@server.com
   cd /opt/kyte-doolittle
   ```

2. **啟動後端（使用 systemd）**
   ```bash
   sudo systemctl start kyte-doolittle-api
   ```

3. **啟動前端（Nginx）**
   ```nginx
   server {
       listen 80;
       server_name hydropathy.example.com;
       root /opt/kyte-doolittle/frontend;
       index index.html;
   }
   ```

---

## ⚠️ 常見問題

### **Q: API 提示「CORS 錯誤」**
A: 確認後端已正確啟動在 `localhost:8000`。若在生產環境，編輯 `src/web_api.py` 的 CORS 設置。

### **Q: 「序列不找到」（UniProtKB）**
A: 檢查 AC/ID 格式。AC 應為 `P12345` 格式（6 位），ID 應為 `NAME_ORGANISM` 格式（如 `TP53_HUMAN`）。

### **Q: 圖表無法顯示**
A: 檢查瀏覽器開發者工具（F12）查看 Console 錯誤。確保 Plotly.js 已正確加載。

### **Q: 計算很慢**
A: 長序列（>1000 aa）可能需要幾秒。若超過 30 秒，檢查網絡連接（若使用 UniProtKB 查詢）。

---

## 📚 參考資源

- **原論文**：`docs/Kyte–Doolittle_Hydropathy_Scale.pdf`
- **疏水性值表**：`docs/Kyte-Doolittle_hydropathy_scale_ values.pdf`
- **API 文檔**：http://localhost:8000/docs

---

## 🔗 相關連結

- 🐙 GitHub：https://github.com/jong-liu/kyte-doolittle
- 📖 UniProtKB：https://www.uniprot.org/
- 📊 Plotly 文檔：https://plotly.com/javascript/

---

**最後更新**：2026-11-07 | **版本**：0.1.0
