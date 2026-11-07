@echo off
REM 啟用 GitHub Pages for kyte-doolittle (Windows)

setlocal enabledelayedexpansion

set REPO_OWNER=jong-liu
set REPO_NAME=kyte-doolittle

echo.
echo 🔧 配置 GitHub Pages...
echo.

REM 檢查 gh 認証
gh auth status >nul 2>&1
if errorlevel 1 (
    echo ❌ 請先執行 gh auth login
    pause
    exit /b 1
)

echo 📝 設置 Pages 源為 master 分支 /frontend...
echo.

REM 使用 GitHub API 設置 Pages
for /f "tokens=2 delims= " %%A in ('gh auth token') do set GH_TOKEN=%%A

curl -s -X POST ^
  -H "Accept: application/vnd.github+json" ^
  -H "Authorization: Bearer %GH_TOKEN%" ^
  https://api.github.com/repos/%REPO_OWNER%/%REPO_NAME%/pages ^
  -d "{\"source\":{\"branch\":\"master\",\"path\":\"/frontend\"}}" >nul

echo ✅ GitHub Pages 配置已提交！
echo.
echo 🌐 你的網站將在以下地址可訪問：
echo    https://%REPO_OWNER%.github.io/%REPO_NAME%/
echo.
echo 提示：部署通常需要 1-2 分鐘。稍後訪問上述 URL 查看前端。
echo.
pause
