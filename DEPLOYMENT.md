# GitHub 推送 & Pages 部署指南

## 第一步：建立 GitHub Repo

### 選項 A：使用 GitHub CLI（推薦）

```bash
# 1. 登入 GitHub
gh auth login
# 按提示選擇：
# - Account: GitHub.com
# - Protocol: HTTPS
# - Auth method: Login with web browser
# (會自動開啟瀏覽器認証)

# 2. 完成認証後，創建 repo
cd "G:\我的雲端硬碟\claude\projects\kyte–doolittle"

gh repo create kyte-doolittle \
  --public \
  --source=. \
  --push \
  --remote=origin \
  --description "Protein Hydropathy Scale Calculator (Kyte-Doolittle Method)"
```

### 選項 B：手動在網頁建立

1. 訪問 https://github.com/new
2. 填寫表單：
   - **Repository name**: `kyte-doolittle`
   - **Description**: `Protein Hydropathy Scale Calculator (Kyte-Doolittle Method, 1982)`
   - **Visibility**: ✓ Public
   - 點擊 **Create repository**

3. 回到終端推送本地代碼：
```bash
cd "G:\我的雲端硬碟\claude\projects\kyte–doolittle"
git push -u origin master
```

---

## 第二步：推送代碼

推送本地所有 commit 到 GitHub：

```bash
cd "G:\我的雲端硬碟\claude\projects\kyte–doolittle"
git push -u origin master
```

預期輸出：
```
Enumerating objects: 20, done.
Counting objects: 100% (20/20), done.
Delta compression using up to 8 threads
Compressing objects: 100% (15/15), done.
Writing objects: 100% (20/20), ...KB, done.
Total 20 (delta 5), reused 0 (delta 0), pack-reused 0
remote: ...
To https://github.com/jong-liu/kyte-doolittle.git
 * [new branch]      master -> master
Branch 'master' set to track remote branch 'master' from 'origin'.
```

---

## 第三步：啟用 GitHub Pages

### 選項 A：使用腳本（自動）

```bash
# Windows
enable-pages.bat

# macOS/Linux
bash enable-pages.sh
```

### 選項 B：手動設置

1. 訪問 https://github.com/jong-liu/kyte-doolittle/settings/pages

2. 在 **Source** 區塊設置：
   - **Branch**: `master`
   - **Folder**: `/ (root)` 或 `/frontend`
   - 點擊 **Save**

3. 等待 1-2 分鐘部署

### 選項 C：使用 GitHub API

```bash
# 需要先登入 gh
gh auth login

# 設置 Pages
curl -s -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $(gh auth token)" \
  https://api.github.com/repos/jong-liu/kyte-doolittle/pages \
  -d '{"source":{"branch":"master","path":"/frontend"}}'
```

---

## 第四步：驗證部署

完成後，訪問：

🌐 **https://jong-liu.github.io/kyte-doolittle/**

應該看到完整的 Kyte–Doolittle 計算器 Web UI。

---

## 🧪 檢查清單

- [ ] Repo 已建立在 GitHub (`jong-liu/kyte-doolittle`)
- [ ] 所有 commit 已推送 (`git push -u origin master` 成功)
- [ ] GitHub Pages 已啟用 (Settings → Pages)
- [ ] 網站可訪問 (https://jong-liu.github.io/kyte-doolittle/)
- [ ] 前端 UI 能正常載入

---

## ⚠️ 常見問題

### **推送時提示「repository not found」**
- ✓ 檢查 Repo 是否已在 GitHub 建立
- ✓ 檢查 remote URL 是否正確：`git remote -v`
- ✓ 檢查 GitHub 認証是否完成

### **Pages 部署失敗**
- ✓ 檢查 Repo Settings → Pages
- ✓ 確認 Branch 選對 (`master`)
- ✓ 確認 Folder 設對 (`/` 或 `/frontend`)
- ✓ 查看 Actions 標籤看部署日誌

### **前端無法連接 API**
- ✓ 開發環境：修改 `frontend/index.html` 的 `API_URL`
- ✓ 生產環境：需要部署後端 API（Vercel/Render/Railway）

---

## 🚀 後續步驟

### 部署後端 API（可選）

如果要在生產環境使用 UniProtKB 查詢功能，需要部署後端：

**推薦方案：Vercel**

```bash
# 1. 安裝 Vercel CLI
npm install -g vercel

# 2. 部署
cd "G:\我的雲端硬碟\claude\projects\kyte–doolittle"
vercel

# 3. 記錄部署 URL（e.g., kyte-doolittle.vercel.app）

# 4. 更新前端 API_URL
# 編輯 frontend/index.html，改成：
# const API_URL = 'https://kyte-doolittle.vercel.app/api';
```

**其他方案：**
- Render.com (免費層)
- Railway.app (免費層)
- Heroku (付費)

---

**祝部署順利！🎉**

最後更新：2026-11-07
