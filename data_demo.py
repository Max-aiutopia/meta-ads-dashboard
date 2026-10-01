#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 示範客戶的組裝層。真實客戶各有一支 data_<slug>.py，只放「這個客戶特有的東西」：
# 素材圖檔與文案、創意庫的篩選維度、起跑線、品牌色。數字和判讀都從 _live/ 讀，排程刷新就好，這支不用改。
import json, os
import dashlive as L
from make_demo_data import BRANDS

D = os.path.dirname(os.path.abspath(__file__))
GRADS = {"hearth": "linear-gradient(120deg,#3b2414,#6b3f22 45%,#d39a5b)",
         "loom": "linear-gradient(120deg,#151519,#3a3a44 45%,#8a7a56)"}


def build(slug):
    b = BRANDS[slug]
    idx = json.load(open(f"{D}/demo_assets/{slug}/index.json", encoding="utf-8"))
    live, _ = L.load(slug)
    by_nm = {c["nm"]: c for c in live["creatives"]}

    assets = {nm: dict(img=a["img"], hook=f"{a['cn']} · {a['pn']}",
                       copy=f"（示範文案）{a['pn']}｜{a['cn']}切角。真實客戶這裡會放從 Meta 逐字抓回的主要文案。")
              for nm, a in idx.items()}

    def perf(nm):
        c = by_nm[nm]
        ok = c["pu"] > 0 and c["roas"] >= b["be"]
        return dict(st=f"{c['pu']} 購 · ROAS {L.roas(c['roas'])}", stc="g" if ok else "o", sp=c["sp"], im=c["im"],
                    ctr=c["ctr"], pu=c["pu"], roas=c["roas"] or None, note="示範資料。")

    lib_ads = [dict(av=a["pk"], avn=a["pn"], c=a["ck"], cn=a["cn"], v="v01", vn="單圖",
                    fname=os.path.basename(a["img"]), hl=a["cn"], angle=f"{a['cn']} · {a['pn']}",
                    file=L.thumb(a["img"], 560), perf=perf(nm)) for nm, a in idx.items()]

    life = live["campaign"]["life"]
    base = dict(rows=[["示範舊批（已關閉）", int(life["sp"] * 0.6), round(life["roas"] * 0.8, 2), int(life["pu"] * 0.5), None, life["ctr"], "off"]],
                sum=["示範起跑線", round(life["roas"] * 0.8, 2), None, int(life["pu"] * 0.5), int(life["sp"] * 0.6)],
                note="起跑線＝新素材上線前的舊批成效，拿來判斷新一批有沒有比較好。")

    return L.build(
        slug=slug, account_id="0000000000", kg=b["kg"], be=b["be"], cpa_cap=None,
        kg_label="目標 ROAS", assets=assets, brand=os.environ.get("DASH_BRAND", "Demo Agency"),
        hero_grad=GRADS[slug], title=f"{b['name']} · 廣告績效檢視台（示範）",
        lib_big=f"{len(lib_ads)} 支素材 · {len(b['products'])} 個產品 × {len(b['angles'])} 個切角",
        lib_avs=[["all", "全部"]] + [[k, n] for k, n in b["products"]],
        lib_cs=[["all", "全部切角"]] + [[k, n] for k, n in b["angles"]],
        lib_ads=lib_ads, base=base, base_big="示範起跑線",
    )
