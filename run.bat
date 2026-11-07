@echo off
REM 啟動 Kyte–Doolittle 應用（開發模式）- Windows

setlocal enabledelayedexpansion

echo.
echo 🚀 啟動 Kyte–Doolittle 應用 (開發模式)
echo ================================================

REM 1. 檢查並安裝依賴
echo.
echo 📦 檢查 Python 依賴...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo    安裝 requirements.txt...
    pip install -q -r requirements.txt
)

REM 2. 啟動後端 API（背景執行）
echo.
echo 🌐 啟動 FastAPI 後端 (http://localhost:8000)...
start "Kyte-Doolittle API" cmd /k "python -m uvicorn src.web_api:app --host 0.0.0.0 --port 8000 --reload"
echo    ✓ 後端已啟動
timeout /t 3 /nobreak

REM 3. 啟動前端伺服器
echo.
echo 🎨 啟動前端伺服器 (http://localhost:8080)...
cd frontend
start "Kyte-Doolittle Frontend" cmd /k "python -m http.server 8080"
cd ..
echo    ✓ 前端已啟動

echo.
echo ================================================
echo ✅ 應用已啟動！
echo.
echo 🌐 訪問：
echo    • 前端 UI：http://localhost:8080
echo    • API 文檔：http://localhost:8000/docs
echo    • API 健康檢查：http://localhost:8000/api/health
echo.
echo 按 Ctrl+C 停止服務（若干視窗會同時關閉）
echo ================================================
echo.
pause
