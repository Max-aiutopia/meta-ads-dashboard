#!/usr/bin/env python3
# 把示範資料建好的檢視台輸出到 docs/，給 GitHub Pages 當線上示範：
#   docs/index.html   總覽＋兩個示範客戶（不加密）
#   docs/locked.html  同一份內容的加密版，示範登入殼（密碼寫在 README）
# 跑法：python3 make_demo_data.py && python3 build_all.py && python3 build_artifact.py \
#       && DASH_PASSWORD=demo-password-123 python3 build_secure.py && python3 publish_demo.py
import os, shutil
D = os.path.dirname(os.path.abspath(__file__))
os.makedirs(f"{D}/docs", exist_ok=True)
frag = open(f"{D}/platform-artifact.html", encoding="utf-8").read()
open(f"{D}/docs/index.html", "w", encoding="utf-8").write(
    '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1"></head>'
    f'<body style="margin:0;height:100vh;display:flex;flex-direction:column">{frag}</body></html>')
shutil.copy(f"{D}/deploy-secure/index.html", f"{D}/docs/locked.html")
print("docs/index.html, docs/locked.html")
