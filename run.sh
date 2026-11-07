#!/bin/bash
# 啟動 Kyte–Doolittle 應用（開發模式）

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "🚀 啟動 Kyte–Doolittle 應用 (開發模式)"
echo "================================================"

# 1. 檢查並安裝依賴
echo "📦 檢查 Python 依賴..."
if ! python -c "import fastapi" 2>/dev/null; then
    echo "   安裝 requirements.txt..."
    pip install -q -r requirements.txt
fi

# 2. 啟動後端 API（背景執行）
echo ""
echo "🌐 啟動 FastAPI 後端 (http://localhost:8000)..."
python -m uvicorn src.web_api:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!
echo "   ✓ 後端已啟動 (PID: $API_PID)"

# 3. 等待 API 就緒
echo "⏳ 等待 API 就緒..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
        echo "   ✓ API 已就緒"
        break
    fi
    sleep 1
done

# 4. 啟動前端伺服器（簡單 HTTP）
echo ""
echo "🎨 啟動前端伺服器 (http://localhost:8080)..."
echo "   前端路徑：$PROJECT_DIR/frontend/"

# 簡單的 Python HTTP 伺服器
cd frontend
python -m http.server 8080 &
FRONTEND_PID=$!
echo "   ✓ 前端已啟動 (PID: $FRONTEND_PID)"

echo ""
echo "================================================"
echo "✅ 應用已啟動！"
echo ""
echo "🌐 訪問："
echo "   • 前端 UI：http://localhost:8080"
echo "   • API 文檔：http://localhost:8000/docs"
echo "   • API 健康檢查：http://localhost:8000/api/health"
echo ""
echo "按 Ctrl+C 停止所有服務"
echo "================================================"

# 等待背景進程
wait $API_PID $FRONTEND_PID
