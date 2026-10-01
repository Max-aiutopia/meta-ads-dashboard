#!/usr/bin/env python3
# 廣告績效檢視台 — 發布版：把「總覽＋各客戶頁」合成一個自包單檔（可放 Netlify 或任何靜態主機）。
# 客戶頁以 iframe 內嵌（JS/CSS 完全隔離）；殼層沿用檢視台視覺系統。
# 客戶分「合作中(active)／已停止(ended)」兩區，首頁切換只顯示該區的卡片。
# 卡片數字自動從 _live/<slug>.json ＋ _live/<slug>_narrative.json 讀：排程刷新數字層，首頁就跟著更新。
# 已停止合作的客戶用凍結快照（frozen），不再更新。
# 跑法：先 python3 build_all.py 再 python3 build_artifact.py
import base64, os, json

D = os.path.dirname(os.path.abspath(__file__))
BRAND = os.environ.get("DASH_BRAND", "Demo Agency")
OUT = f"{D}/platform-artifact.html"
INDEX = f"{D}/index.html"

def b64(fname):
    with open(f"{D}/{fname}", "rb") as f:
        return base64.b64encode(f.read()).decode()

# ── 客戶名冊 ──────────────────────────────────────────────────────────────
# live=<slug>：卡片的數據日／KPI／狀態行自動從 _live/<slug>.json ＋ _live/<slug>_narrative.json 取。
# be=損益線（ROAS 上色門檻：>=be*1.5 綠、>=be 金、否則紅）。
# frozen=已停止合作的凍結快照（upd/kpi/st 手寫，不再更新）。
# 下面兩個都是虛構的示範客戶（數字由 make_demo_data.py 產生）。
CLIENTS = [
 dict(key="hb", name="Hearth & Bean 咖啡", file="hearth.html", status="active", live="hearth", be=2.0,
      sub="耳掛＋濾掛禮盒 · 示範客戶（虛構資料）",
      band="linear-gradient(90deg,#6b3f22,#d39a5b)"),
 dict(key="lm", name="Loom & Line 服飾", file="loom.html", status="ended", be=2.2,
      sub="寬褲＋短 T · 示範客戶（虛構資料）",
      band="linear-gradient(90deg,#2b2b30,#6f6f7a)",
      pill="⛔ 已停止更新",
      frozen=dict(upd="09-01",
                  kpi=[("最後 ROAS", "1.62", "r"), ("累計花費／購買", "38,200 / 41", ""), ("狀態", "已停止", "")],
                  st="⛔ 示範用凍結快照：已停止追蹤的客戶保留最後數據，不再更新。")),
]

# ── 自動取數（數字層／敘事層）────────────────────────────────────────────
def _roas_cls(v, be):
    return "g" if v >= be * 1.5 else ("o" if v >= be else "r")

def enrich(c):
    """live 客戶的 upd/kpi/st 從 _live JSON 自動補；ended 客戶用 frozen 凍結快照。"""
    if c.get("frozen"):
        c.update(c["frozen"]); return c
    slug = c["live"]
    live = json.load(open(f"{D}/_live/{slug}.json", encoding="utf-8"))
    nar = json.load(open(f"{D}/_live/{slug}_narrative.json", encoding="utf-8"))
    cam, be = live["campaign"], c["be"]
    life, w7 = cam["life"]["roas"], cam["w7"]["roas"]
    c["upd"] = live["as_of"][5:]                        # 2026-07-30 → 07-30
    c["kpi"] = [("全期 ROAS", f"{life:.2f}", _roas_cls(life, be)),
                ("過去 7 天", f"{w7:.2f}", _roas_cls(w7, be)),
                ("現役素材", f"{len(live['creatives'])} 支", "")]
    c["st"] = nar["note_html"]
    return c

CLIENTS = [enrich(c) for c in CLIENTS]
SRC = {c["key"]: b64(c["file"]) for c in CLIENTS}
actives = [c for c in CLIENTS if c["status"] == "active"]
endeds  = [c for c in CLIENTS if c["status"] == "ended"]
ordered = actives + endeds
stamp_date = max(c["upd"] for c in (actives or CLIENTS))
first_grp = "active" if actives else "ended"

def card(c, as_link=False):
    """as_link=True → <a href=檔案>（本機總覽頁用）；False → <button data-go>（發布版 iframe 切換用）。"""
    tag = "a" if as_link else "button"
    attrs = f'href="{c["file"]}"' if as_link else f'data-go="{c["key"]}"'
    ended = c["status"] == "ended"
    badge = f'<span class="pill">{c.get("pill", "⛔ 已停止合作")}</span>' if ended else ''
    mrow = "".join(f'<span class="m"><i>{l}</i><b class="{cc}">{v}</b></span>' for l, v, cc in c["kpi"])
    return f'''<{tag} class="cc{' ended' if ended else ''}" {attrs}>
 <span class="band" style="background:{c["band"]}"></span>
 <span class="cb"><span class="cname">{c["name"]}{badge}</span><span class="csub">{c["sub"]} · 數據至 {c["upd"]}</span>
 <span class="mrow">{mrow}</span>
 <span class="cst">{c["st"]}</span><span class="go">{'開啟檢視台 →' if as_link else '進入檢視台 →'}</span></span>
</{tag}>'''

# 分頁籤：合作中在前、已停止在後
tabs = '<button class="tab on" data-t="home">總覽</button>' + "".join(
    f'<button class="tab" data-t="{c["key"]}">{c["name"]}{"（已停）" if c["status"]=="ended" else ""}</button>' for c in ordered)

SHELL_CSS = """
:root{--paper:#F2EEE8;--ink:#241f19;--ink2:#6b6155;--line:#ddd3c4;--card:#FFFCF6;--green:#3A9647;--gold:#E89A12;--red:#D6283A;--shadow:0 10px 34px rgba(50,40,25,.12)}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{background:var(--paper);color:var(--ink);font-family:"PingFang TC","Noto Sans TC",system-ui,sans-serif;display:flex;flex-direction:column}
.top{background:linear-gradient(120deg,#1c1712,#3d2f1f 60%,#8a6a2f);color:#fff;padding:10px 18px;display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.brand{font-size:12px;letter-spacing:.34em;text-transform:uppercase;opacity:.85;font-weight:600}
.tabs{display:flex;gap:6px;flex-wrap:wrap}
.tab{border:1px solid rgba(255,255,255,.35);background:transparent;color:#fff;padding:6px 16px;border-radius:30px;font-size:13.5px;cursor:pointer;font-family:inherit}
.tab.on{background:#fff;color:var(--ink);border-color:#fff;font-weight:600}
.tab:focus-visible{outline:2px solid #fff;outline-offset:2px}
.stamp{margin-left:auto;font-size:11.5px;opacity:.75}
.panel{flex:1;display:none;min-height:0}
.panel.on{display:block}
#p-home{overflow-y:auto;padding:34px 22px 40px}
.homewrap{max-width:980px;margin:0 auto}
.homewrap h1{font-family:"Songti TC",Georgia,serif;font-size:38px;font-weight:600;text-wrap:balance}
.homewrap .sub{color:var(--ink2);font-size:14.5px;margin:4px 0 22px}
.seg{display:inline-flex;gap:4px;background:var(--card);border:1px solid var(--line);border-radius:30px;padding:4px;margin-bottom:22px}
.segb{border:none;background:transparent;color:var(--ink2);padding:8px 18px;border-radius:24px;font-size:13.5px;cursor:pointer;font-family:inherit;font-weight:600}
.segb.on{background:var(--ink);color:#fff}
.segb:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
.ccgrid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
/* ⚠️ 必要：作者樣式的 display:grid 會蓋掉 [hidden] 的 UA display:none，沒這行「合作中／已停止」切換會失效 */
.ccgrid[hidden]{display:none}
.cc{text-align:left;border:1px solid var(--line);background:var(--card);border-radius:18px;overflow:hidden;box-shadow:var(--shadow);cursor:pointer;padding:0;font-family:inherit;color:var(--ink);transition:transform .16s,box-shadow .16s;display:block;text-decoration:none}
.cc:hover{transform:translateY(-4px);box-shadow:0 18px 44px rgba(50,40,25,.2)}
.cc:focus-visible{outline:3px solid var(--gold);outline-offset:2px}
.cc.ended{opacity:.72}
.cc.ended .band{filter:grayscale(.5)}
.pill{display:inline-block;font-family:"PingFang TC",sans-serif;font-size:10.5px;font-weight:600;color:#8a5a00;background:#f3e2c2;border-radius:20px;padding:2px 9px;margin-left:9px;vertical-align:middle}
.band{display:block;height:8px}
.cb{display:block;padding:18px 20px 20px}
.cname{display:block;font-family:"Songti TC",Georgia,serif;font-size:22px;font-weight:600}
.csub{display:block;font-size:12px;color:var(--ink2);margin-top:2px}
.mrow{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin:14px 0 11px}
.m{background:var(--paper);border:1px solid var(--line);border-radius:11px;padding:8px 11px;display:block}
.m i{display:block;font-size:10.5px;color:var(--ink2);font-style:normal}
.m b{font-size:17px;font-family:"Songti TC",Georgia,serif}
.m b.g{color:var(--green)}.m b.o{color:var(--gold)}.m b.r{color:var(--red)}
.cst{display:block;font-size:12px;line-height:1.65;color:var(--ink2)}
.go{display:block;margin-top:12px;font-size:13px;font-weight:600}
.empty{color:var(--ink2);font-size:13.5px;padding:20px 4px}
.hnote{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 18px;margin-top:22px;font-size:12.5px;color:var(--ink2);line-height:1.8}
iframe{width:100%;height:100%;border:none;display:block;background:var(--paper)}
@media(max-width:760px){.ccgrid{grid-template-columns:1fr}.homewrap h1{font-size:28px}.stamp{display:none}}
@media(prefers-reduced-motion:reduce){.cc{transition:none}}
"""

def home_body(as_link=False):
    a = "".join(card(c, as_link) for c in actives) or '<div class="empty">目前沒有合作中的客戶。</div>'
    e = "".join(card(c, as_link) for c in endeds) or '<div class="empty">還沒有已停止追蹤的客戶。</div>'
    return f"""<div class="homewrap">
 <h1>廣告績效檢視台 · 客戶總覽</h1>
 <div class="sub">選一個商場進入它的檢視台 · 每個客戶＝獨立廣告帳號＋同一套觀測系統 · 數據由排程從 Meta Ads 實抓</div>
 <div class="seg" role="tablist" aria-label="合作狀態切換">
  <button class="segb{' on' if first_grp=='active' else ''}" data-g="active" role="tab" aria-selected="{str(first_grp=='active').lower()}">目前合作中 · {len(actives)}</button>
  <button class="segb{' on' if first_grp=='ended' else ''}" data-g="ended" role="tab" aria-selected="{str(first_grp=='ended').lower()}">已停止追蹤 · {len(endeds)}</button>
 </div>
 <div class="ccgrid" data-grp="active"{' hidden' if first_grp!='active' else ''}>{a}</div>
 <div class="ccgrid" data-grp="ended"{' hidden' if first_grp!='ended' else ''}>{e}</div>
 <div class="hnote"><b>使用說明</b>：上方切「目前合作中／已停止追蹤」＝<b>只顯示該區的客戶</b>；或用頂端分頁、點卡片進入客戶檢視台。已停止追蹤的客戶保留可回顧、資料凍結不再更新。頭條 KPI 只計「投放中」活動；素材卡皆可點開看版位／年齡／性別拆解與完整文案。要最新數據：讓排程重抓數字層後重跑建置，本頁重新發布、網址不變。</div>
</div>"""

SEG_JS = """document.querySelectorAll('.segb').forEach(b=>b.onclick=()=>{
 document.querySelectorAll('.segb').forEach(x=>{const on=x===b;x.classList.toggle('on',on);x.setAttribute('aria-selected',on)});
 document.querySelectorAll('.ccgrid').forEach(g=>g.hidden=(g.dataset.grp!==b.dataset.g));
});"""

HTML = f"""<meta charset="utf-8"><title>{BRAND} · 廣告績效檢視台</title>
<style>{SHELL_CSS}</style>
<div class="top">
 <span class="brand">{BRAND}</span>
 <nav class="tabs" aria-label="客戶切換">{tabs}</nav>
 <span class="stamp">數據至 {stamp_date}</span>
</div>
<div class="panel on" id="p-home">{home_body()}</div>
{"".join(f'<div class="panel" id="p-{c["key"]}"><iframe title="{c["name"]} 檢視台" loading="lazy"></iframe></div>' for c in ordered)}
<script>
const SRC={json.dumps(SRC)};
const loaded={{}};
function go(t){{
 document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('on',b.dataset.t===t));
 document.querySelectorAll('.panel').forEach(p=>p.classList.toggle('on',p.id==='p-'+t));
 if(SRC[t]&&!loaded[t]){{const bytes=Uint8Array.from(atob(SRC[t]),c=>c.charCodeAt(0));const url=URL.createObjectURL(new Blob([bytes],{{type:'text/html;charset=utf-8'}}));document.querySelector('#p-'+t+' iframe').src=url;loaded[t]=true}}
}}
document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>go(b.dataset.t));
document.querySelectorAll('.cc').forEach(c=>c.onclick=()=>go(c.dataset.go));
{SEG_JS}
</script>"""
open(OUT, "w", encoding="utf-8").write(HTML)
print("built", OUT, f"{os.path.getsize(OUT)//1024} KB")

# ── 本機用的獨立總覽頁（_dashboard/index.html）──────────────────────────
# 各客戶頁 hero 的「← 客戶總覽」連到這裡。同一份 CLIENTS 資料生成，避免與發布版說法不一致。
IDX = f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{BRAND} · 客戶總覽</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23241f19'/%3E%3Ctext x='32' y='45' font-size='38' text-anchor='middle' fill='%23E89A12' font-family='Georgia,serif'%3ES%3C/text%3E%3C/svg%3E">
<style>{SHELL_CSS}
body{{display:block}} #p-home{{padding:34px 22px 40px}}
</style></head><body>
<div class="top">
 <span class="brand">{BRAND}</span>
 <span class="stamp">數據至 {stamp_date} · 本機總覽</span>
</div>
<div id="p-home">{home_body(as_link=True)}</div>
<script>{SEG_JS}</script></body></html>"""
open(INDEX, "w", encoding="utf-8").write(IDX)
print("built", INDEX, f"{os.path.getsize(INDEX)//1024} KB")
