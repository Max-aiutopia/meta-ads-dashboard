#!/bin/bash
# 一鍵重建＋加密＋部署到 Netlify。
# 需要：netlify CLI 已登入、環境變數 DASH_PASSWORD（至少 12 字）與 NETLIFY_SITE_ID。
set -e
cd "$(dirname "$0")"
: "${DASH_PASSWORD:?請先設定 DASH_PASSWORD}"
: "${NETLIFY_SITE_ID:?請先設定 NETLIFY_SITE_ID}"
echo "▸ 1/4 重建客戶頁…" && python3 build_all.py
echo "▸ 2/4 合成單檔…"   && python3 build_artifact.py
echo "▸ 3/4 加密…"       && python3 build_secure.py
mkdir -p deploy-secure/site && cp deploy-secure/index.html deploy-secure/site/
echo "▸ 4/4 部署到 Netlify…"
netlify deploy --prod --dir "deploy-secure/site" --site "$NETLIFY_SITE_ID"
