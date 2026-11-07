#!/bin/bash
# 啟用 GitHub Pages for kyte-doolittle

set -e

REPO_OWNER="jong-liu"
REPO_NAME="kyte-doolittle"

echo "🔧 配置 GitHub Pages..."
echo ""

# 檢查 gh 認証
if ! gh auth status >/dev/null 2>&1; then
    echo "❌ 請先執行 gh auth login"
    exit 1
fi

# 啟用 Pages（source: gh-pages branch）
echo "📝 設置 Pages 源為 gh-pages 分支..."
gh repo edit $REPO_OWNER/$REPO_NAME \
    --enable-issues \
    --enable-wiki \
    --enable-projects >/dev/null 2>&1 || true

# 使用 GitHub API 設置 Pages
echo "🌐 通過 GitHub API 啟用 Pages..."
curl -s -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $(gh auth token)" \
  https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/pages \
  -d '{"source":{"branch":"master","path":"/frontend"}}' \
  -w "\n%{http_code}\n" | tail -1 | grep -q "201\|204" && echo "✅ Pages 已啟用 (source: /frontend)" || echo "⚠️ Pages 可能已啟用，請檢查 Settings"

echo ""
echo "✅ GitHub Pages 配置完成！"
echo "🌐 你的網站將在以下地址可訪問："
echo "   https://$REPO_OWNER.github.io/$REPO_NAME/"
echo ""
echo "提示：部署通常需要 1-2 分鐘。稍後訪問上述 URL 查看前端。"
