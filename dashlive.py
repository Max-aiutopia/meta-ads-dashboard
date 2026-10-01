#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 廣告績效檢視台 —「數字層 JSON → dashlib 的 C」共用組裝器。
#
# 為什麼有這支：每個客戶的組裝邏輯都一樣，各抄一份就是各抄一份 bug。
# 這支把「三層資料 → 卡片／表格／散點／排行／趨勢」的機械部分收在一起，
# data_<slug>.py 只要給「這個客戶特有的東西」（素材圖檔/文案、創意庫、起跑線、品牌色）。
#
# 資料分層（排程可直接刷新）：
#   數字層 _live/<slug>.json           ← 排程重寫（Meta 實抓）
#   敘事層 _live/<slug>_narrative.json ← 排程重寫（判讀文字）
#   拆解層 _live/<slug>_det.json       ← 排程重寫（版位/年齡/性別 breakdown）
#   素材層 _live/<slug>_assets.json    ← 排程遇到新素材時寫（img/hook/copy），會蓋掉 .py 裡的 ASSETS
#   歷史層 _history/<slug>/daily.json  ← 排程 merge（趨勢圖數據源）
import json as _json, os as _os, urllib.parse as _url
from dashlib import thumb

import os as __os
DIR = __os.path.dirname(__os.path.abspath(__file__))

# ── 格式化 ──────────────────────────────────────────────────────────────
def money(n): return f"NT${int(round(n)):,}"
def pct(x): return f"{x:.2f}%"
def roas(r): return f"{r:.2f}" if r else "—"
def cpa(sp, pu): return f"NT${int(round(sp/pu)):,}" if pu else "—"

# ── 缺圖佔位 ────────────────────────────────────────────────────────────
def placeholder(label):
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="480" height="480">'
           '<rect width="100%" height="100%" fill="#EFE7D8"/>'
           '<rect x="10" y="10" width="460" height="460" fill="none" stroke="#c9bda6" stroke-width="3" stroke-dasharray="12 10"/>'
           '<text x="50%" y="45%" font-family="PingFang TC,Noto Sans TC,sans-serif" font-size="30" fill="#a9967a" text-anchor="middle">待補圖</text>'
           f'<text x="50%" y="55%" font-family="PingFang TC,Noto Sans TC,sans-serif" font-size="20" fill="#8a7a5e" text-anchor="middle">{label}</text></svg>')
    return "data:image/svg+xml;utf8," + _url.quote(svg)

def img_or_placeholder(path, label, w=480):
    return thumb(path, w) if (path and _os.path.exists(path)) else placeholder(label)

# ── 讀三層 ──────────────────────────────────────────────────────────────
def load(slug):
    live = _json.load(open(f"{DIR}/_live/{slug}.json", encoding="utf-8"))
    nar = _json.load(open(f"{DIR}/_live/{slug}_narrative.json", encoding="utf-8"))
    return live, nar

def merge_overrides(slug, assets):
    """把 _live/<slug>_assets.json（新素材圖文）與 _live/<slug>_det.json（拆解）併進 ASSETS。JSON 勝出。"""
    aj = f"{DIR}/_live/{slug}_assets.json"
    if _os.path.exists(aj):
        for k, v in _json.load(open(aj, encoding="utf-8")).items():
            assets.setdefault(k, {}).update(v)
    dj = f"{DIR}/_live/{slug}_det.json"
    if _os.path.exists(dj):
        for k, v in _json.load(open(dj, encoding="utf-8")).items():
            assets.setdefault(k, {})["det"] = v
    return assets

def daily_series(slug):
    """回傳 (campaign 日序列, 依素材名查日序列的函式)。"""
    h = f"{DIR}/_history/{slug}/daily.json"
    d = _json.load(open(h, encoding="utf-8")) if _os.path.exists(h) else {"campaign": {}, "ads": {}}
    def ser(m):
        return [[k[5:].lstrip("0").replace("-0", "/").replace("-", "/"), v[0], v[1], v[2]] for k, v in sorted(m.items())]
    ads = d.get("ads", {})
    def find(nm):
        for cand in (nm, nm + "_1x1"):
            if cand in ads: return ser(ads[cand])
        return None
    return ser(d.get("campaign", {})), find

# ── 分類：先看花費夠不夠判，再看成效 ─────────────────────────────────────
#   規則整理自 Meta 投放實務常見的關單原則：
#     花費 < 2× 目標 CPA            → 還沒測夠，不關
#     花到 2× 仍 0 購買              → 可關（沒有 CPA 上限的帳號一律只觀察，不建議關）
#     有購買但 CPA > 1.5× 目標 CPA   → 可關
#     成效在目標的 50% 以內          → 觀察，先不關
#     花到 3× 且仍差 50% 以上        → 可關
#   ⚠️ 低花費、高 ROAS 的素材多半是「supporting ad」（最後點擊歸因把功勞算給它），
#      留著、不加預算、不列入放大名單。
def classifier(kg, cpa_cap=None, big_spend=800, min_tested=None):
    gate2 = (2 * cpa_cap) if cpa_cap else (min_tested or 100)   # 未達 2× CPA 不關
    gate3 = (3 * cpa_cap) if cpa_cap else gate2 * 1.5           # 3× 且仍差 50% 才關
    def cls(sp, ro, pu):
        # ① 達標的先分「概念」與「supporting」：花費在帳號前 10% 才算贏家
        if pu > 0 and ro >= kg:
            return "win" if sp >= big_spend else "pot"
        # ② 未達 2× 目標 CPA：還沒測夠
        if sp < gate2:
            return "watch"
        # ③ 花到 2× 仍 0 購買（缺 ATC/IC 資料，交付時要標明這一點）
        #    ⚠️ 沒有 King Goal／CPA 上限的帳號：關單門檻未定義 → 一律不回 lose（不得建議關掉）
        if pu == 0:
            return "lose" if cpa_cap else "watch"
        # ④ 有購買但 CPA > 1.5× 目標 CPA
        if cpa_cap and (sp / pu) > cpa_cap * 1.5:
            return "lose"
        # ⑤ 結果在 KPI 50% 以內：不急著關
        if ro >= kg * 0.5:
            return "watch"
        if not cpa_cap:
            return "watch"
        return "lose" if sp >= gate3 else "watch"
    return cls

CLS_LABELS = [["🏆 概念", "win", "#3A9647"], ["🤝 supporting（留但不加預算）", "pot", "#2f6f8f"],
              ["⚠️ 未達關單門檻／觀察", "watch", "#E89A12"], ["❌ 已過門檻可關", "lose", "#D6283A"]]

# ── 主組裝 ──────────────────────────────────────────────────────────────
def build(*, slug, account_id, kg, assets, hero_grad, title, sub=None, brand="Ads Dashboard",
          be=None, cpa_cap=None, kg_label="King Goal", big_spend=None,
          xray_h2="Static X-ray · 現役靜態", xray_big=None,
          lib_big, lib_avs, lib_cs, lib_ads,
          base, base_big, leader_big="誰在賺錢，一目了然",
          ins_big="這個帳號怎麼贏", scat_big=None, trendc_big=None,
          det_range=None, lib_range="", trendc_note=None, vassets=None, va_dir=None,
          extra=None):
    """回傳可直接餵給 dashlib.render 的 C。assets = {素材名: {img(絕對路徑), hook, copy, det}}。"""
    live, nar = load(slug)
    assets = merge_overrides(slug, assets)
    # 贏家＝花費在帳號前 10% 的素材 → 用花費分佈的 90 百分位當門檻，
    # 而不是寫死一個金額（不同客戶花費級別差很多）。
    _sp = sorted((c.get("sp14", c["sp"]) for c in live["creatives"]), reverse=True)
    if big_spend is None and _sp:
        _k = max(1, int(len(_sp) * 0.10))
        big_spend = _sp[_k - 1]
    cls = classifier(kg, cpa_cap=cpa_cap, big_spend=big_spend or 800)
    cr = live["creatives"]
    stat = sorted([c for c in cr if c["kind"] == "s"], key=lambda c: -c["sp"])
    vid = sorted([c for c in cr if c["kind"] == "v"], key=lambda c: -c["sp"])
    tag = lambda nm: nar["tags"].get(nm, ["", "b"])

    def scard(c):
        a = assets.get(c["nm"], {}); t = tag(c["nm"])
        return dict(img=img_or_placeholder(a.get("img"), c["nm"]), nm=c["nm"], pr=c["product"],
                    hk=a.get("hook", ""), sp=money(c["sp"]), ct=pct(c["ctr"]), pu=str(c["pu"]),
                    cpa=cpa(c["sp"], c["pu"]), ro=roas(c["roas"]), tag=t[0], tc=t[1],
                    det=a.get("det"), copy=a.get("copy", ""))
    XRAY = [scard(c) for c in stat]

    # 影片（有 video_funnel 才組）
    VIDS = []
    vf = live.get("video_funnel") or {}
    if vid and vf:
        def scale(d):
            lo, hi = min(d.values()), max(d.values())
            return {k: (0 if hi == lo else round((v - lo) / (hi - lo) * 100)) for k, v in d.items()}
        vk = [c["vkey"] for c in vid]
        hs = scale({k: (vf[k]["p25"] / vf[k]["im"] if vf[k]["im"] else 0) for k in vk})
        ws = scale({k: (vf[k]["p50"] / vf[k]["p25"] if vf[k]["p25"] else 0) for k in vk})
        cs = scale({c["vkey"]: c["roas"] for c in vid})
        for c in vid:
            k = c["vkey"]; f = vf[k]; a = (vassets or {}).get(k, {}); t = tag(c["nm"])
            hook = f["p25"] / f["im"] if f["im"] else 0
            fin = f["p100"] / f["p25"] if f["p25"] else 0
            VIDS.append(dict(img=img_or_placeholder(f"{va_dir}/poster_{k}.jpg" if va_dir else None, c["nm"]),
                             nm=c["nm"], hk=a.get("hook", ""), sp=money(c["sp"]), ro=roas(c["roas"]),
                             cpa=cpa(c["sp"], c["pu"]), pu=str(c["pu"]), ct=pct(c["ctr"]), tpc=money(f["tpc"]),
                             im=f["im"], s3=f["s3"], p25=f["p25"], p50=f["p50"], p75=f["p75"], p100=f["p100"],
                             hook=f"{hook*100:.0f}%", fin=f"{fin*100:.0f}%", tag=t[0], tc=t[1],
                             diag=a.get("diag", ""), hs=hs[k], ws=ws[k], cs=cs[k],
                             mgr=f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={account_id}&selected_ad_ids={a.get('id','')}"))

    def rows_of(cards_src):
        out = []
        for c in cards_src:
            t = tag(c["nm"])
            out.append([c["nm"], money(c["sp"]), f"{c['im']:,}", pct(c["ctr"]), str(c["pu"]),
                        roas(c["roas"]) + (" · " + t[0] if t[0] else ""), t[1]])
        return out
    STBL = dict(head=["現役靜態", "花費", "曝光", "CTR", "購買", "狀態"],
                rows=rows_of(stat), note=nar["notes"].get("stbl", ""))
    VTBL = (dict(head=["現役影片", "花費", "曝光", "CTR", "購買", "狀態"],
                 rows=rows_of(vid), note=nar["notes"].get("vtbl", "")) if VIDS else None)

    # 散點圖
    nm2ref = {}
    for i, c in enumerate(XRAY): nm2ref[c["nm"]] = ("x", i)
    for i, v in enumerate(VIDS): nm2ref[v["nm"]] = ("v", i)
    # 主判讀窗＝近 14 天（用 lifetime 累計判讀會被早期數字拖住）。
    # 數字層若有 sp14/roas14/pu14 就用它們分類與畫散點；沒有才退回累計。
    def _w14(c):
        return (c.get("sp14", c["sp"]), c.get("roas14", c["roas"]), c.get("pu14", c["pu"]))
    pts = [dict(nm=c["nm"], sp=_w14(c)[0], ro=_w14(c)[1], pu=_w14(c)[2], kind=c["kind"], zone="act",
                cls=cls(*_w14(c)),
                rt=nm2ref.get(c["nm"], ("", 0))[0], ri=nm2ref.get(c["nm"], ("", 0))[1]) for c in cr]
    missing = [p["nm"] for p in pts if not p["rt"]]
    if missing: raise SystemExit(f"[{slug}] scat 名字對不到卡片: {missing}")
    cnt = lambda k: sum(1 for p in pts if p["cls"] == k)
    SCAT = dict(pts=pts, target=kg, target2=be, tlab=kg_label, t2lab="不虧錢 BE",
                counters=[[lab, cnt(key), col] for lab, key, col in CLS_LABELS],
                note=f"計數為現役 {len(pts)} 支。" + nar["notes"].get("scat", ""))

    # 排行榜（有轉換者）
    lead = sorted([c for c in cr if c["pu"] > 0 and c["roas"] > 0], key=lambda c: -c["roas"])
    emoji = lambda c: ("🎬 " if c["kind"] == "v" else "") + c["nm"]
    LEADER = dict(rows=[[i + 1, emoji(c), c["product"], roas(c["roas"]), cpa(c["sp"], c["pu"]),
                         str(c["pu"]), money(c["sp"]), tag(c["nm"])[0], tag(c["nm"])[1]]
                        for i, c in enumerate(lead)],
                  note=nar["notes"].get("leader", ""))

    cam_series, find_series = daily_series(slug)
    n_prod = len({c["product"] for c in cr})

    C = dict(
        out=f"{DIR}/{slug}.html",
        title=title, brand=brand, h1="廣告績效檢視台", sub=sub or nar["sub"], hero_grad=hero_grad,
        meta_html=nar["meta_html"], note_html=nar["note_html"], kpis=nar["kpis"], banner=nar["banner"],
        xray=XRAY, xray_h2=xray_h2,
        xray_big=xray_big or f"{len(XRAY)} 支投放中 · {n_prod} 個產品 · 累計至 {live['as_of']}",
        stbl=STBL,
        scat=SCAT, scat_big=scat_big or f"全帳號 {len(pts)} 支 · 花費 × ROAS · 該擴量誰、該關誰，一眼定位",
        leader=LEADER, leader_big=leader_big,
        ins=nar["ins"], ins_big=ins_big, iter=nar["iter"],
        lib_big=lib_big, lib_avs=lib_avs, lib_cs=lib_cs, lib_ads=lib_ads,
        base=base, base_big=base_big,
        texts=dict(det_range=det_range or f"區間：卡片數字與抽屜內版位/年齡/性別拆解皆＝帳號歷史→{live['as_of']} 累計（由排程自動重建）。",
                   lib_range=lib_range),
        footer_html=nar["footer_html"],
        trendc=dict(rows=cam_series, target=kg, target2=be, tlab=kg_label,
                    note=trendc_note or (f"紅線＝{kg_label} {kg:.2f}"
                         + (f"、細虛線＝不虧錢 BE {be:.2f}" if be else "")
                         + f"。最右端為當日盤中值（歸因未回填，會往上修）。數據源 _history/{slug}/daily.json，排程自動累積。")),
        trendc_big=trendc_big or "帳號口徑 · 逐日花費（柱）與當日 ROAS（線）",
    )
    if VIDS:
        C.update(vids=VIDS, vtbl=VTBL,
                 vids_h2="Video X-ray · 現役影片",
                 vids_big=f"{len(VIDS)} 支投放中 · 點卡片看留存漏斗＋完整數據")
    if nar.get("batchtbl"):
        C["batchtbl"] = dict(head=["批次", "花費", "支數", "購買", "ROAS", "組成／結論"],
                             rows=[r[:7] for r in nar["batchtbl"]], note=nar["notes"].get("batch", ""))
    C["trenda"] = {}
    for c in XRAY + VIDS:
        s = find_series(c["nm"])
        if s: C["trenda"][c["nm"]] = s
    if extra: C.update(extra)
    return C
