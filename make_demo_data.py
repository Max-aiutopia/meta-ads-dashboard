#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 產生示範用的假資料：兩個虛構品牌，數字全部由固定亂數種子產生，跟任何真實客戶無關。
# 寫出來的檔案格式，跟真實排程寫的一模一樣：
#   _live/<slug>.json            數字層（活動／素材／廣告組合／漏斗）
#   _live/<slug>_narrative.json  敘事層（判讀文字、KPI、洞察、下一輪決策）
#   _live/<slug>_det.json        拆解層（每支素材的版位／年齡／性別）
#   _history/<slug>/daily.json   歷史層（逐日 [花費, 購買, ROAS]，趨勢圖用）
#   demo_assets/<slug>/*.png     素材縮圖（用 Pillow 畫的示意圖）
# 用法：python3 make_demo_data.py
import json, os, random, datetime as dt
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
FONT = next((f for f in ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Medium.ttc",
                         "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"] if os.path.exists(f)), None)

BRANDS = {
    "hearth": dict(
        name="Hearth & Bean 咖啡", seed=7, be=2.0, kg=3.0, as_of="2026-09-30", start="2026-09-03",
        products=[("drip", "耳掛咖啡 10 入"), ("gift", "濾掛禮盒")],
        angles=[("c1", "早晨儀式"), ("c2", "辦公室續命"), ("c3", "送禮不踩雷")],
        colors=[(107, 63, 34), (211, 154, 91), (60, 42, 30)],
    ),
    "loom": dict(
        name="Loom & Line 服飾", seed=11, be=2.2, kg=3.2, as_of="2026-09-01", start="2026-08-04",
        products=[("wide", "打褶寬褲"), ("tee", "重磅短 T")],
        angles=[("c1", "棚拍"), ("c2", "街拍"), ("c3", "UGC 自拍")],
        colors=[(43, 43, 48), (111, 111, 122), (160, 150, 130)],
    ),
}


def draw_asset(path, title, sub, color):
    im = Image.new("RGB", (640, 640), color)
    d = ImageDraw.Draw(im)
    for i in range(0, 640, 32):
        d.line([(i, 0), (0, i)], fill=tuple(min(255, c + 14) for c in color), width=2)
    d.rounded_rectangle([60, 360, 580, 580], 28, fill=(255, 252, 246))
    if FONT:
        d.text((90, 390), title, font=ImageFont.truetype(FONT, 52), fill=(36, 31, 25))
        d.text((90, 470), sub, font=ImageFont.truetype(FONT, 34), fill=(107, 97, 85))
        d.text((90, 520), "DEMO · 示範素材", font=ImageFont.truetype(FONT, 24), fill=(160, 150, 130))
    im.save(path)


def r2(x): return round(x, 2)


def make(slug, b):
    rnd = random.Random(b["seed"])
    os.makedirs(f"{D}/_live", exist_ok=True)
    os.makedirs(f"{D}/_history/{slug}", exist_ok=True)
    os.makedirs(f"{D}/demo_assets/{slug}", exist_ok=True)
    aov = rnd.randint(520, 980)

    creatives, det, tags, assets = [], {}, {}, {}
    n = 0
    for pi, (pk, pn) in enumerate(b["products"]):
        for ci, (ck, cn) in enumerate(b["angles"]):
            n += 1
            nm = f"{n:02d}_{pk}_{cn}"
            sp = rnd.choice([380, 900, 1800, 3200, 5200, 8600]) + rnd.randint(0, 400)
            ctr = r2(rnd.uniform(0.9, 3.4))
            im_ = int(sp / rnd.uniform(0.11, 0.19))
            roas = r2(max(0.0, rnd.gauss(b["kg"] * 0.9, 1.3))) if sp > 600 else r2(rnd.choice([0.0, 0.0, 4.8]))
            pu = int(round(sp * roas / aov))
            roas = r2(pu * aov / sp) if pu else 0.0
            sp14 = int(sp * rnd.uniform(0.45, 0.8)); pu14 = int(pu * rnd.uniform(0.4, 0.8))
            creatives.append(dict(nm=nm, product=pn, pack=f"Pack0{pi+1}", kind="s", sp=sp, im=im_, ctr=ctr,
                                  pu=pu, roas=roas, sp14=sp14, pu14=pu14,
                                  roas14=r2(pu14 * aov / sp14) if pu14 else 0.0, freq=r2(rnd.uniform(1.1, 2.4))))
            img = f"{D}/demo_assets/{slug}/{nm}.png"
            draw_asset(img, pn, cn, b["colors"][ci])
            assets[nm] = dict(pk=pk, pn=pn, ck=ck, cn=cn, img=img)
            def split(labels):
                w = [rnd.random() + 0.2 for _ in labels]; s = sum(w)
                out = []
                for lab, x in zip(labels, w):
                    s_ = int(sp * x / s); p_ = int(round(pu * x / s))
                    out.append([lab, s_, p_, r2(p_ * aov / s_) if p_ and s_ else None])
                return sorted(out, key=lambda r: -r[1])
            det[nm] = dict(pos=split(["動態 Feed", "IG Reels", "IG 限動", "Threads", "FB 限動"]),
                           age=split(["18-24", "25-34", "35-44", "45-54", "55+"]),
                           gen=split(["女", "男", "未知"]))
            tags[nm] = (["🏆 主力", "g"] if roas >= b["kg"] and sp > 2500 else
                        ["👀 觀察", "o"] if roas >= b["be"] or sp < 1200 else ["❌ 可關", "r"])

    tot = lambda k: sum(c[k] for c in creatives)
    sp, pu = tot("sp"), tot("pu")
    clicks = int(sum(c["im"] * c["ctr"] / 100 for c in creatives))
    life_roas = r2(pu * aov / sp)
    live = dict(
        _comment="示範資料（make_demo_data.py 產生，虛構）",
        as_of=b["as_of"], check_date=b["as_of"][5:].replace("-", "/").lstrip("0"),
        ranges=dict(y="昨天", w7="過去 7 天"),
        campaign=dict(
            life=dict(sp=sp, im=tot("im"), clicks=clicks, ctr=r2(clicks / tot("im") * 100), cpc=int(sp / clicks), pu=pu, roas=life_roas),
            y=dict(sp=int(sp / 26), im=int(tot("im") / 26), clicks=int(clicks / 26), ctr=r2(clicks / tot("im") * 100), cpc=int(sp / clicks), pu=max(1, pu // 26), roas=r2(life_roas * 1.08)),
            w7=dict(sp=int(sp / 4), im=int(tot("im") / 4), clicks=int(clicks / 4), ctr=r2(clicks / tot("im") * 100), cpc=int(sp / clicks), pu=pu // 4, roas=r2(life_roas * 1.12)),
            w14=dict(sp=tot("sp14"), pu=tot("pu14"), roas=r2(tot("pu14") * aov / tot("sp14")), aov=aov,
                     cpa=int(tot("sp14") / max(1, tot("pu14"))), freq=1.6, cpm=210, ctr=r2(clicks / tot("im") * 100))),
        creatives=creatives, video_funnel={},
        adsets=[dict(pack=f"Pack0{i+1}", product=pn, status="live", sp=sum(c["sp"] for c in creatives if c["product"] == pn),
                     im=sum(c["im"] for c in creatives if c["product"] == pn),
                     pu=sum(c["pu"] for c in creatives if c["product"] == pn), roas=0, start=b["start"][5:])
                for i, (_, pn) in enumerate(b["products"])],
        step1=dict(days_delivered=26, daily_spend_usd=40.0, window_required_days=14, days_elapsed=26, ready_to_judge=True, judge_date=b["start"]),
    )
    json.dump(live, open(f"{D}/_live/{slug}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(det, open(f"{D}/_live/{slug}_det.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    best = max(creatives, key=lambda c: c["roas"] * (c["sp"] > 2500))
    worst = max((c for c in creatives if c["pu"] == 0 or c["roas"] < b["be"]), key=lambda c: c["sp"], default=creatives[-1])
    money = lambda v: f"NT${v:,}"
    nar = dict(
        _comment="示範資料（虛構）",
        check_date=live["check_date"],
        sub=f"{b['name']} · 示範客戶（虛構資料）· {len(creatives)} 支素材 × {len(b['products'])} 個產品",
        meta_html=f"<span>示範資料</span><span>·</span><span>數據至 {b['as_of']}</span>",
        note_html=f"累計 <b>{money(sp)}</b>／<b>{pu}</b> 筆購買／ROAS <b>{life_roas:.2f}</b>（損益線 {b['be']:.1f}）· 主力素材 <code>{best['nm']}</code>",
        kpis=[["累計花費", money(sp), f"{len(creatives)} 支素材"], ["累計購買", str(pu), f"平均客單 {money(aov)}"],
              ["全期 ROAS", f"{life_roas:.2f}", f"損益線 {b['be']:.1f}"], ["近 14 天 ROAS", f"{live['campaign']['w14']['roas']:.2f}", "主判讀窗"]],
        banner=dict(bg="linear-gradient(120deg,#2f3d33,#3e5a45 55%,#6f5a3a)",
                    html=f"這是<b>示範資料</b>：數字由 <code>make_demo_data.py</code> 產生。真實使用時，排程每幾天從 Meta Ads 抓一次，重寫數字層與敘事層，檢視台跟著重建。"),
        tags=tags,
        batchtbl=[["首波測試", money(sp), str(len(creatives)), str(pu), f"{life_roas:.2f}", "示範用批次彙總", "g" if life_roas >= b["be"] else "r"]],
        ins=[["🏆 誰在賺錢", f"<code>{best['nm']}</code>", "green",
              f"花費 {money(best['sp'])}、ROAS {best['roas']:.2f}，花費在帳號前段又守住目標，是這批的概念贏家。"],
             ["❌ 誰在燒錢", f"<code>{worst['nm']}</code>", "red",
              f"花費 {money(worst['sp'])}、ROAS {worst['roas']:.2f}，在損益線以下。設了 CPA 上限的帳號，花到 2× 目標 CPA 仍沒改善就會被判「可關」。"],
             ["👀 低花費高 ROAS 不等於該加碼", "supporting ad", "gold",
              "花費很少、ROAS 很高的素材，多半是最後點擊歸因把功勞算給它。留著，但不列入放大名單。"]],
        iter=[["下一輪要做 📋", "r", "依分類直接動作", [f"關掉 <code>{worst['nm']}</code>", f"<code>{best['nm']}</code> 的切角做 2–3 個新變體", "預算先不加，等新變體跑滿 14 天再判"]],
              ["可以測的假設 🔬", "g", "從數據來的，不是憑空猜", ["CTR 高但購買少的切角：先查落地頁", "同一產品只留 3–4 支素材，避免小預算被拆太散"]]],
        notes=dict(stbl="示範表格。", vtbl="", scat="分類規則見 dashlive.classifier。", batch="", leader="依 ROAS 排序，只列有購買的素材。"),
        footer_html="示範資料（虛構）· 由 make_demo_data.py 產生，與任何真實客戶無關。",
    )
    json.dump(nar, open(f"{D}/_live/{slug}_narrative.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # 歷史層：近 28 天逐日 [花費, 購買, ROAS]
    end = dt.date.fromisoformat(b["as_of"])
    camp, ads = {}, {c["nm"]: {} for c in creatives}
    for i in range(28):
        day = (end - dt.timedelta(days=27 - i)).isoformat()
        s_ = int(sp / 28 * rnd.uniform(0.6, 1.4)); p_ = int(round(s_ * life_roas * rnd.uniform(0.6, 1.4) / aov))
        camp[day] = [s_, p_, r2(p_ * aov / s_) if s_ else 0]
        for c in creatives:
            s2 = int(c["sp"] / 28 * rnd.uniform(0.4, 1.6)); p2 = int(round(s2 * c["roas"] * rnd.uniform(0.5, 1.5) / aov))
            ads[c["nm"]][day] = [s2, p2, r2(p2 * aov / s2) if s2 else 0]
    json.dump(dict(updated=b["as_of"], note="示範資料", campaign=camp, ads=ads),
              open(f"{D}/_history/{slug}/daily.json", "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(assets, open(f"{D}/demo_assets/{slug}/index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{slug}: {len(creatives)} creatives, spend {sp:,}, ROAS {life_roas}")


if __name__ == "__main__":
    for slug, b in BRANDS.items():
        make(slug, b)
