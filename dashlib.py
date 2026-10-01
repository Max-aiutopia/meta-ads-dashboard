#!/usr/bin/env python3
# 廣告績效檢視台 — 共用模板。所有客戶頁由此 render；改這裡＝所有客戶一起變。
# 用法：import dashlib; dashlib.render(C)  其中 C=客戶資料 dict（見 data_*.py）。
import json, base64, io
from PIL import Image

def thumb(path, w=520):
    im = Image.open(path).convert("RGB")
    r = w / im.width
    im = im.resize((w, int(im.height * r)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=80)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()

def vidb64(path):
    return "data:video/mp4;base64," + base64.b64encode(open(path, "rb").read()).decode()

CSS = r"""
:root{--paper:#F4EEE3;--paper2:#EFE7D8;--ink:#241f19;--ink2:#6b6155;--line:#e0d6c4;--red:#D6283A;--gold:#E89A12;--green:#3A9647;--blue:#2f6f8f;--card:#FFFCF6;--shadow:0 8px 30px rgba(60,40,20,.10)}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--paper);color:var(--ink);font-family:"PingFang TC","Noto Sans TC","Hiragino Sans GB",system-ui,sans-serif;line-height:1.6;-webkit-font-smoothing:antialiased}
.serif{font-family:"Songti TC",Georgia,"Times New Roman",serif}
.wrap{max-width:1180px;margin:0 auto;padding:0 28px}
.hero{position:relative;overflow:hidden;color:#fff;padding:54px 0 46px}
.hero:after{content:"";position:absolute;inset:0;background:radial-gradient(circle at 80% -10%,rgba(255,255,255,.22),transparent 45%)}
.hero .wrap{position:relative}
.brandmark{font-size:13px;letter-spacing:.42em;text-transform:uppercase;opacity:.85;font-weight:600}
.brandmark a{color:inherit;text-decoration:none}
.hero h1{font-size:54px;line-height:1.05;font-weight:600;margin:10px 0 6px}
.hero .sub{font-size:18px;opacity:.92;font-weight:300}
.hero .meta{margin-top:16px;font-size:13px;opacity:.85;display:flex;gap:16px;flex-wrap:wrap}
.note{display:inline-flex;align-items:center;gap:8px;margin-top:16px;background:rgba(0,0,0,.2);border:1px solid rgba(255,255,255,.28);padding:8px 15px;border-radius:30px;font-size:12.5px}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;background:#fff}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:-34px 0 8px;position:relative;z-index:3}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px 18px;box-shadow:var(--shadow)}
.kpi .lab{font-size:12px;color:var(--ink2)}
.kpi .val{font-size:30px;font-weight:600;margin-top:3px;font-family:"Songti TC",Georgia,serif}
.kpi .val small{font-size:15px;color:var(--ink2)}
.sec{margin:44px 0 8px}
.sec h2{font-size:13px;letter-spacing:.34em;text-transform:uppercase;color:var(--ink2);font-weight:600;display:flex;align-items:center;gap:14px}
.sec h2:after{content:"";flex:1;height:1px;background:var(--line)}
.sec .big{font-size:27px;font-weight:600;margin-top:6px}
.controls{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 6px;align-items:center}
.chip{border:1px solid var(--line);background:var(--card);color:var(--ink2);padding:7px 15px;border-radius:30px;font-size:13.5px;cursor:pointer;transition:.15s}
.chip:hover{border-color:#c9b48f}.chip.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.spacer{flex:1}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin-top:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:18px;overflow:hidden;box-shadow:var(--shadow);cursor:pointer;transition:transform .18s,box-shadow .18s;display:flex;flex-direction:column}
.card:hover{transform:translateY(-4px);box-shadow:0 16px 40px rgba(60,40,20,.16)}
.thumb{position:relative;aspect-ratio:1;overflow:hidden}
.thumb img{width:100%;height:100%;object-fit:cover;display:block}
.tags{position:absolute;top:10px;left:10px;display:flex;gap:6px;flex-wrap:wrap}
.tag{background:rgba(28,24,20,.72);color:#fff;font-size:11px;padding:3px 9px;border-radius:20px;backdrop-filter:blur(3px)}
.ver{position:absolute;top:10px;right:10px;font-size:11px;font-weight:600;padding:4px 10px;border-radius:20px;color:#fff;background:#8a8174}
.body{padding:13px 15px 15px}
.body .hl{font-weight:600;font-size:15px;line-height:1.4;min-height:42px}
.body .angle{font-size:12px;color:var(--ink2);margin-top:3px}
.pend{display:flex;align-items:center;gap:7px;margin-top:11px;border-top:1px solid var(--line);padding-top:10px;font-size:12px;color:var(--ink2)}
.pd{width:7px;height:7px;border-radius:50%;background:#cdbf9f}
footer{margin:48px 0 40px;color:var(--ink2);font-size:12.5px;text-align:center;line-height:1.9}
.scrim{position:fixed;inset:0;background:rgba(30,22,14,.5);opacity:0;pointer-events:none;transition:.2s;z-index:40}.scrim.on{opacity:1;pointer-events:auto}
.drawer{position:fixed;top:0;right:0;height:100%;width:min(440px,92vw);background:var(--paper);box-shadow:-10px 0 40px rgba(0,0,0,.25);transform:translateX(100%);transition:.26s cubic-bezier(.4,0,.2,1);z-index:50;overflow-y:auto}.drawer.on{transform:none}
.drawer .dimg{width:100%;aspect-ratio:1;object-fit:cover}.drawer .dbody{padding:22px 24px 40px}
.drawer .x{position:absolute;top:14px;right:16px;width:36px;height:36px;border-radius:50%;background:rgba(0,0,0,.5);color:#fff;border:none;font-size:18px;cursor:pointer;z-index:2}
.mgrid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:16px 0}
.mcell{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:11px 13px}.mcell .ml{font-size:11px;color:var(--ink2)}.mcell .mv{font-size:20px;font-weight:600;font-family:"Songti TC",Georgia,serif;color:var(--ink)}
.livebanner{color:#fff;border-radius:16px;padding:15px 20px;margin-top:16px;box-shadow:var(--shadow);font-size:13.5px;line-height:1.75}
.livebanner b{font-weight:700}
.btbl{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:16px;overflow:hidden;box-shadow:var(--shadow);margin-top:16px;font-size:13.5px}
.btbl th{background:var(--paper2);text-align:left;padding:11px 14px;font-size:11px;letter-spacing:.06em;color:var(--ink2);text-transform:uppercase;font-weight:600}
.btbl th:not(:nth-child(2)),.btbl td.num{text-align:right;font-variant-numeric:tabular-nums}
.btbl td{padding:11px 14px;border-top:1px solid var(--line)}
.btbl td.rk{color:var(--ink2);width:34px;text-align:right}
.btbl td.roas{font-weight:700}.btbl td.roas.g{color:var(--green)}.btbl td.roas.o{color:var(--gold)}.btbl td.roas.r{color:var(--red)}
.btbl tr.sum td{background:var(--paper2);font-weight:600;border-top:2px solid #d8cbb0}
.btbl th.tl{text-align:left}.btbl th.tr{text-align:right}
.tscroll{overflow-x:auto;margin-top:16px;border-radius:16px;box-shadow:var(--shadow);-webkit-overflow-scrolling:touch}
.tscroll .btbl{min-width:640px;margin-top:0;box-shadow:none}
.livedot{display:inline-block;font-size:10px;color:#fff;background:var(--green);padding:2px 7px;border-radius:20px;margin-left:6px;vertical-align:middle}
.bnote{font-size:12.5px;color:var(--ink2);margin-top:10px;line-height:1.7}
.xgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:18px}
.xc{background:var(--card);border:1px solid var(--line);border-radius:16px;overflow:hidden;box-shadow:var(--shadow);display:flex;flex-direction:column;cursor:pointer;transition:transform .18s,box-shadow .18s}
.xc:hover{transform:translateY(-4px);box-shadow:0 16px 40px rgba(60,40,20,.16)}
.xthumb{position:relative;aspect-ratio:4/5;overflow:hidden}
.xthumb img{width:100%;height:100%;object-fit:cover;display:block}
.xtag{position:absolute;top:10px;left:10px;font-size:11px;font-weight:600;color:#fff;padding:3px 9px;border-radius:20px;background:#8a8174;backdrop-filter:blur(3px)}
.xtag.g{background:var(--green)}.xtag.o{background:var(--gold)}.xtag.r{background:var(--red)}.xtag.b{background:var(--blue)}
.xbd{padding:12px 13px 14px}
.xnm{font-weight:600;font-size:14px;line-height:1.3}
.xhk{font-size:11.5px;color:var(--ink2);margin:3px 0 11px;min-height:30px}
.xmg{display:grid;grid-template-columns:repeat(5,1fr);gap:4px;text-align:center;border-top:1px solid var(--line);padding-top:10px}
.xm i{display:block;font-size:9.5px;color:var(--ink2);font-style:normal;margin-bottom:2px}
.xm b{font-size:13px;font-family:"Songti TC",Georgia,serif}
.xm b.g{color:var(--green)}.xm b.o{color:var(--gold)}.xm b.r{color:var(--red)}
.itwrap{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-top:16px}
.itcol{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px 18px;box-shadow:var(--shadow)}
.itcol .itsub{font-size:12.5px;color:var(--ink2);margin:8px 0 6px}
.itcol ul{margin:0;padding-left:17px}.itcol li{font-size:13px;margin:5px 0;line-height:1.5}
.itag{font-size:12.5px;font-weight:600;color:#fff;padding:4px 12px;border-radius:20px;display:inline-block}
.itag.g{background:var(--green)}.itag.o{background:var(--gold)}.itag.r{background:var(--red)}.itag.b{background:var(--blue)}
.dbody h4{font-size:12px;letter-spacing:.18em;color:var(--ink2);text-transform:uppercase;margin:18px 0 8px;font-weight:600}
.hrow{display:grid;grid-template-columns:64px 1fr auto;gap:8px;align-items:center;margin:5px 0;font-size:12px}
.hrow .hl{color:var(--ink2)}
.hrow .hbar{height:9px;background:var(--paper2);border-radius:5px;overflow:hidden}
.hrow .hbar i{display:block;height:100%;background:#7c6fc0;border-radius:5px}
.hrow .hv{font-variant-numeric:tabular-nums;white-space:nowrap}
.hrow .hv b.g{color:var(--green)}.hrow .hv b.o{color:var(--gold)}.hrow .hv b.r{color:var(--red)}
.adcopy{font-size:12.5px;line-height:1.8;color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;white-space:pre-wrap}
.xnote{font-size:11.5px;color:var(--ink2);margin-top:12px;line-height:1.6}
.lgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(265px,1fr));gap:14px;margin-top:16px}
.lcard{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px 18px;box-shadow:var(--shadow)}
.lcard .t{font-size:12px;color:var(--ink2)}.lcard .r{font-size:30px;font-weight:700;font-family:"Songti TC",Georgia,serif}
.lcard .d{font-size:12px;color:var(--ink2);margin-top:4px;line-height:1.65}
.tabbar{position:sticky;top:0;z-index:25;background:var(--paper);border-bottom:1px solid var(--line);margin-top:20px;display:flex;gap:2px;overflow-x:auto;-webkit-overflow-scrolling:touch}
.tbtn{border:none;background:none;padding:13px 15px 11px;font-size:14.5px;color:var(--ink2);cursor:pointer;font-family:inherit;white-space:nowrap;border-bottom:2.5px solid transparent;font-weight:500}
.tbtn:hover{color:var(--ink)}
.tbtn.on{color:var(--ink);font-weight:700;border-bottom-color:var(--gold)}
.tabpane{display:none}.tabpane.on{display:block}
.scatwrap{position:relative}
.stip{display:none;position:absolute;z-index:30;background:var(--card);border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow);padding:8px;gap:9px;align-items:center;pointer-events:none;max-width:250px}
.stip img{width:54px;height:54px;object-fit:cover;border-radius:8px}
.stip .tt{font-size:12px;line-height:1.5}
.sdot{cursor:pointer}
.hrow2{grid-template-columns:150px 1fr 44px}
.sth{cursor:pointer;user-select:none;white-space:nowrap}.sth:hover{color:var(--ink)}.sarr{font-size:9px;margin-left:2px;opacity:.75}
.vplay{position:absolute;inset:0;margin:auto;width:46px;height:46px;border-radius:50%;background:rgba(20,17,14,.62);color:#fff;display:flex;align-items:center;justify-content:center;font-size:17px;backdrop-filter:blur(2px);pointer-events:none}
.vbtn{display:block;text-align:center;margin-top:14px;padding:11px;border-radius:12px;background:var(--ink);color:#fff;font-size:13.5px;font-weight:600;text-decoration:none}
.vbtn:hover{opacity:.9}
.dvid{width:100%;max-height:58vh;background:#141110;object-fit:contain;display:block}
@media(max-width:900px){.kpis{grid-template-columns:repeat(2,1fr)}.grid,.xgrid{grid-template-columns:repeat(2,1fr)}.lgrid{grid-template-columns:1fr}.hero h1{font-size:38px}.btbl{font-size:12px}.btbl th,.btbl td{padding:9px 8px}}
"""

JS = r"""
const $=s=>document.querySelector(s);
function roascls(v){const f=parseFloat(v);return isNaN(f)?'':(f>=3?'g':f>=2?'o':'r')}
function kpis(){$('#kpis').innerHTML=KPIS.map(c=>`<div class="kpi"><div class="lab">${c[0]}</div><div class="val">${c[1]}<small> ${c[2]}</small></div></div>`).join('')}
function banner(){$('#livebanner').innerHTML=`<div class="livebanner" style="background:${BANNER.bg}">${BANNER.html}</div>`}
const TSTATE={};
function dnum(x){const f=parseFloat(String(x).replace(/[^0-9.\-]/g,''));return isNaN(f)?-1:f}
function mkTbl(id,D){if(!D)return;const el=document.getElementById(id);if(!el)return;const S=[1,2,3,4];const st=TSTATE[id];
 let idx=D.rows.map((r,i)=>i);
 if(st)idx.sort((a,b)=>(dnum(D.rows[b][st.c])-dnum(D.rows[a][st.c]))*(st.d==='desc'?1:-1)||a-b);
 const rows=idx.map(i=>{const r=D.rows[i];const cls=r[6]==='g'?'g':r[6]==='r'?'r':'o';return `<tr><td>${r[0]}</td><td class="num">${r[1]}</td><td class="num">${r[2]}</td><td class="num">${r[3]}</td><td class="num">${r[4]}</td><td class="num roas ${cls}">${r[5]}</td></tr>`}).join('');
 const head=D.head.map((h,c)=>{if(!S.includes(c))return `<th class="${c===0?'tl':'tr'}">${h}</th>`;const ar=st&&st.c===c?(st.d==='desc'?'▼':'▲'):'⇅';return `<th class="sth tr" data-c="${c}" title="點擊排序：降冪→升冪→還原">${h}<span class="sarr">${ar}</span></th>`}).join('');
 el.innerHTML=`<div class="tscroll"><table class="btbl"><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table></div><div class="bnote">${D.note||''}</div>`;
 el.querySelectorAll('.sth').forEach(e=>{e.onclick=()=>{const c=+e.dataset.c;const cur=TSTATE[id];
  TSTATE[id]=(!cur||cur.c!==c)?{c,d:'desc'}:(cur.d==='desc'?{c,d:'asc'}:null);mkTbl(id,D)}})}
function delivery(){mkTbl('delivery',typeof DELIV!=='undefined'&&DELIV?DELIV:null)}
function hbars(rows){const mx=Math.max(...rows.map(r=>r[1]));return rows.map(r=>{const w=Math.max(2,Math.round(r[1]/mx*100));const v=r[3]==null?`NT$${r[1].toLocaleString()} · ${r[2]}購`:`NT$${r[1].toLocaleString()} · ${r[2]}購 · <b class="${r[3]>=3?'g':r[3]>=2?'o':'r'}">ROAS ${r[3].toFixed(2)}</b>`;
 return `<div class="hrow"><span class="hl">${r[0]}</span><span class="hbar"><i style="width:${w}%"></i></span><span class="hv">${v}</span></div>`}).join('')}
function xcard(a,gi){return `<div class="xc" data-x="${gi}"><div class="xthumb"><img src="${a.img}" loading="lazy"><span class="xtag ${a.tc}">${a.tag}</span></div><div class="xbd"><div class="xnm">${a.nm}</div><div class="xhk">${a.pr} · ${a.hk}</div><div class="xmg"><div class="xm"><i>花費</i><b>${a.sp}</b></div><div class="xm"><i>ROAS</i><b class="${roascls(a.ro)}">${a.ro}</b></div><div class="xm"><i>CPA</i><b>${a.cpa}</b></div><div class="xm"><i>購買</i><b>${a.pu}</b></div><div class="xm"><i>CTR</i><b>${a.ct}</b></div></div></div></div>`}
function xray(){const ex=document.getElementById('xray');if(ex)ex.innerHTML=XRAY.map((a,i)=>xcard(a,i)).join('');
 const e2=document.getElementById('xarch');
 if(e2&&typeof XARCH!=='undefined')e2.innerHTML=XARCH.map((a,i)=>xcard(a,XRAY.length+i)).join('');
 document.querySelectorAll('#xray .xc, #xarch .xc').forEach(e=>e.onclick=()=>openX(+e.dataset.x))}
function openX(i){const a=i<XRAY.length?XRAY[i]:XARCH[i-XRAY.length];
 const mid=a.det?`<h4>版位拆解 · 這支素材在哪賺錢</h4>${hbars(a.det.pos)}<h4>年齡 · 誰在買</h4>${hbars(a.det.age)}<h4>性別</h4>${hbars(a.det.gen)}<div class="xnote">※ 單筆購買的高 ROAS 屬小樣本雜訊，看方向別看絕對值。${TEXTS.det_range}</div>`:`<div class="xnote">此支花費/樣本太小，逐支拆解暫無統計意義；拿到投遞量後刷新即補上（版位/年齡/性別）。</div>`;
 $('#drawer').innerHTML=`<button class="x" onclick="closeD()">×</button><img class="dimg" src="${a.img}"><div class="dbody"><span class="xtag ${a.tc}" style="position:static;display:inline-block">${a.tag}</span><h3 class="serif" style="font-size:21px;font-weight:600;margin:10px 0 2px">${a.nm}</h3><div style="color:var(--ink2);font-size:13px">${a.pr} · ${a.hk}</div><div class="mgrid">${[["花費",a.sp],["ROAS",a.ro],["CPA",a.cpa],["購買",a.pu],["CTR",a.ct]].map(m=>`<div class="mcell"><div class="ml">${m[0]}</div><div class="mv">${m[1]}</div></div>`).join('')}</div>${mid}${sparkBlock(a.nm)}<h4>文案 Primary Text</h4><div class="adcopy">${a.copy}</div></div>`;
 $('#scrim').classList.add('on');$('#drawer').classList.add('on')}
function vbars(v){const rows=[["曝光",v.im],["看到25%",v.p25],["看到50%",v.p50],["看到75%",v.p75],["看完100%",v.p100]];const mx=rows[0][1];
 return rows.map((r,i)=>{const w=Math.max(2,Math.round(r[1]/mx*100));const pct=(r[1]/mx*100).toFixed(i?1:0)+'%';
 return `<div class="hrow"><span class="hl">${r[0]}</span><span class="hbar"><i style="width:${w}%;background:#2f6f8f"></i></span><span class="hv">${r[1].toLocaleString()} · ${pct}</span></div>`}).join('')}
function vids(){const el=$('#vids');if(!el||typeof VIDS==='undefined'||!VIDS.length)return;
 el.innerHTML=VIDS.map((v,i)=>`<div class="xc" data-v="${i}"><div class="xthumb"><img src="${v.img}" loading="lazy"><span class="xtag ${v.tc}">${v.tag}</span><span class="vplay">▶</span></div><div class="xbd"><div class="xnm">${v.nm}</div><div class="xhk">${v.hk}</div><div class="xmg"><div class="xm"><i>花費</i><b>${v.sp}</b></div><div class="xm"><i>ROAS</i><b class="${roascls(v.ro)}">${v.ro}</b></div><div class="xm"><i>購買</i><b>${v.pu}</b></div><div class="xm"><i>Hook</i><b>${v.hook}</b></div><div class="xm"><i>完看</i><b>${v.fin}</b></div></div></div></div>`).join('');
 el.querySelectorAll('.xc').forEach(e=>e.onclick=()=>openV(+e.dataset.v))}
function openV(i){const v=VIDS[i];
 const media=v.vid?`<video class="dvid" controls playsinline preload="none" poster="${v.img}" src="${v.vid}"></video>`:`<img class="dimg" src="${v.img}">`;
 $('#drawer').innerHTML=`<button class="x" onclick="closeD()">×</button>${media}<div class="dbody"><span class="xtag ${v.tc}" style="position:static;display:inline-block">${v.tag}</span><h3 class="serif" style="font-size:21px;font-weight:600;margin:10px 0 2px">${v.nm}</h3><div style="color:var(--ink2);font-size:13px">${v.hk}</div><div class="mgrid">${[["花費",v.sp],["ROAS",v.ro],["CPA",v.cpa],["購買",v.pu],["CTR",v.ct],["Hook率(3秒/曝光)",v.hook],["3秒播放",v.s3.toLocaleString()],["ThruPlay成本",v.tpc]].map(m=>`<div class="mcell"><div class="ml">${m[0]}</div><div class="mv">${m[1]}</div></div>`).join('')}</div><h4>留存漏斗 · 觀眾看到哪裡走掉</h4>${vbars(v)}<div class="xnote">${v.diag}</div>${scoreBlock(v)}${sparkBlock(v.nm)}<a class="vbtn" href="${v.mgr}" target="_blank" rel="noopener">在 Meta 廣告管理員開這支廣告 ↗</a><div class="xnote">上方播放器為 480p 壓縮預覽（投放版畫質更高）；留存數據區間 7/16 上線→2026-07-18。</div></div>`;
 $('#scrim').classList.add('on');$('#drawer').classList.add('on')}
function scat(){const el=document.getElementById('scat');if(!el||typeof SCAT==='undefined'||!SCAT)return;
 const P=SCAT.pts,W=1000,H=520,L=64,R=30,T=20,B=46;
 const xmin=Math.log10(8),xmax=Math.log10(40000);
 const ymax=Math.ceil(Math.max(...P.map(p=>p.ro),SCAT.target,SCAT.target2||0)+0.5);
 const X=v=>L+(Math.log10(Math.max(v,8))-xmin)/(xmax-xmin)*(W-L-R);
 const Y=v=>T+(1-v/ymax)*(H-T-B);
 let s='<svg viewBox="0 0 '+W+' '+H+'" style="width:100%;height:auto;display:block">';
 for(let r=0;r<=ymax;r++){s+=`<line x1="${L}" y1="${Y(r)}" x2="${W-R}" y2="${Y(r)}" stroke="#e0d6c4" stroke-width="1"/><text x="${L-8}" y="${Y(r)+4}" text-anchor="end" font-size="12" fill="#6b6155">${r}</text>`}
 [10,100,1000,5000,10000,30000].forEach(t=>{s+=`<line x1="${X(t)}" y1="${T}" x2="${X(t)}" y2="${H-B}" stroke="#e0d6c4" stroke-dasharray="2 4"/><text x="${X(t)}" y="${H-B+18}" text-anchor="middle" font-size="11" fill="#6b6155">${t>=1000?(t/1000)+'k':t}</text>`});
 // 兩條線：target2＝BE 不虧錢底線（細虛線）、target＝King Goal 可規模化門檻（粗線，判定用這條）
 if(SCAT.target2){const y2=Y(SCAT.target2);
  s+=`<line x1="${L}" y1="${y2}" x2="${W-R}" y2="${y2}" stroke="#a8946c" stroke-width="1.5" stroke-dasharray="3 4"/><text x="${L+6}" y="${y2-6}" font-size="11.5" fill="#8a7a56">${SCAT.t2lab||'不虧錢 BE'} ${SCAT.target2.toFixed(2)}</text>`}
 s+=`<line x1="${L}" y1="${Y(SCAT.target)}" x2="${W-R}" y2="${Y(SCAT.target)}" stroke="#D6283A" stroke-width="2.5"/><text x="${W-R}" y="${Y(SCAT.target)-7}" text-anchor="end" font-size="12" fill="#D6283A" font-weight="700">${SCAT.tlab||'損益線'} ${SCAT.target.toFixed(2)}</text>`;
 s+=`<text x="${(L+W-R)/2}" y="${H-6}" text-anchor="middle" font-size="12" fill="#6b6155">花費 NT$（對數刻度）→</text>`;
 s+=`<text x="16" y="${T+8}" font-size="12" fill="#6b6155" transform="rotate(-90 16 ${T+8}) translate(-60 0)">ROAS ↑</text>`;
 const CC={win:'#3A9647',pot:'#2f6f8f',watch:'#E89A12',lose:'#D6283A'};
 P.forEach((p,i)=>{const r=Math.min(17,6+Math.sqrt(p.pu)*1.9);
  s+=`<circle class="sdot" data-i="${i}" cx="${X(p.sp)}" cy="${Y(p.ro)}" r="${r}" fill="${CC[p.cls]}" fill-opacity="${p.zone==='act'?0.88:0.30}" stroke="${CC[p.cls]}" stroke-width="1.5" ${p.zone==='arch'?'stroke-dasharray="3 2"':''}/>`;
  if(p.kind==='v')s+=`<text x="${X(p.sp)}" y="${Y(p.ro)+3.5}" text-anchor="middle" font-size="9" fill="#fff" pointer-events="none">▶</text>`});
 s+='</svg>';
 const cn=SCAT.counters.map(c=>`<span class="chip" style="cursor:default;border-color:transparent;background:${c[2]};color:#fff;font-weight:600">${c[0]} ${c[1]}</span>`).join('');
 el.innerHTML=`<div class="controls" style="margin-top:14px">${cn}<span class="spacer"></span><span style="font-size:12px;color:var(--ink2)">實心＝現役 · 虛框＝已關 · ▶＝影片 · 圈越大購買越多 · 點圓點開完整分析</span></div><div class="card" style="cursor:default;padding:10px 8px 4px">${s}</div><div class="bnote">${SCAT.note}</div><div class="stip" id="stip"></div>`;
 el.querySelectorAll('.sdot').forEach(d=>{
  d.onclick=()=>{const p=P[+d.dataset.i];if(p.rt==='v')openV(p.ri);else if(p.rt==='x')openX(p.ri)};
  d.onmouseenter=ev=>{const p=P[+d.dataset.i];const c=p.rt==='v'?VIDS[p.ri]:(p.ri<XRAY.length?XRAY[p.ri]:XARCH[p.ri-XRAY.length]);
   const tip=document.getElementById('stip');tip.innerHTML=`${c&&c.img?`<img src="${c.img}">`:''}<div class="tt"><b>${p.nm}</b><br>NT$${p.sp.toLocaleString()} · ${p.pu} 購 · ROAS ${p.ro||'—'}</div>`;
   const rect=el.getBoundingClientRect();tip.style.display='flex';
   tip.style.left=Math.min(ev.clientX-rect.left+14,rect.width-255)+'px';tip.style.top=(ev.clientY-rect.top+12)+'px'};
  d.onmouseleave=()=>{document.getElementById('stip').style.display='none'}})}
function trendsvg(rows,w,h,tg,tg2){const TG=tg||2;const L=52,R=14,T=12,B=30;
 const smax=Math.max(...rows.map(r=>r[1]),1);const rmax=Math.max(...rows.map(r=>r[3]),TG,tg2||0,2.5);
 const n=rows.length,step=(w-L-R)/n,bw=Math.max(3,step*0.6);
 let s=`<svg viewBox="0 0 ${w} ${h}" style="width:100%;height:auto;display:block">`;
 const ty=T+(1-Math.min(TG,rmax)/rmax)*(h-T-B);
 if(tg2){const y2=T+(1-Math.min(tg2,rmax)/rmax)*(h-T-B);
  s+=`<line x1="${L}" y1="${y2}" x2="${w-R}" y2="${y2}" stroke="#a8946c" stroke-dasharray="3 4" stroke-width="1.2"/><text x="${L-6}" y="${y2+4}" text-anchor="end" font-size="10" fill="#8a7a56">${tg2.toFixed(1)}</text>`}
 s+=`<line x1="${L}" y1="${ty}" x2="${w-R}" y2="${ty}" stroke="#D6283A" stroke-dasharray="6 5" stroke-width="1.5"/>`;
 rows.forEach((r,i)=>{const x=L+i*step+(step-bw)/2;const bh=r[1]/smax*(h-T-B);
  s+=`<rect x="${x.toFixed(1)}" y="${(h-B-bh).toFixed(1)}" width="${bw.toFixed(1)}" height="${bh.toFixed(1)}" rx="2" fill="#cdbf9f" fill-opacity="0.8"><title>${r[0]}｜NT$${r[1].toLocaleString()}｜${r[2]} 購｜ROAS ${r[3]}</title></rect>`});
 const pts=rows.map((r,i)=>`${(L+i*step+step/2).toFixed(1)},${(T+(1-Math.min(r[3],rmax)/rmax)*(h-T-B)).toFixed(1)}`).join(' ');
 s+=`<polyline points="${pts}" fill="none" stroke="#2f6f8f" stroke-width="2.5" stroke-linejoin="round"/>`;
 rows.forEach((r,i)=>{if(r[2]>0){const cx=L+i*step+step/2,cy=T+(1-Math.min(r[3],rmax)/rmax)*(h-T-B);
  s+=`<circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="3.2" fill="#2f6f8f"><title>${r[0]}｜${r[2]} 購｜ROAS ${r[3]}</title></circle>`}});
 const lab=Math.ceil(n/12);rows.forEach((r,i)=>{if(i%lab===0||i===n-1)s+=`<text x="${(L+i*step+step/2).toFixed(1)}" y="${h-B+16}" text-anchor="middle" font-size="10" fill="#6b6155">${r[0]}</text>`});
 s+=`<text x="${L-6}" y="${T+9}" text-anchor="end" font-size="10" fill="#6b6155">$${smax>=1000?(smax/1000).toFixed(1)+'k':smax}</text>`;
 s+=`<text x="${L-6}" y="${ty+4}" text-anchor="end" font-size="10" fill="#D6283A" font-weight="600">${TG.toFixed(1)}</text>`;
 return s+'</svg>'}
function trendc(){const el=document.getElementById('trendc');if(!el||typeof TRENDC==='undefined'||!TRENDC||!TRENDC.rows.length)return;
 el.innerHTML=`<div class="card" style="cursor:default;padding:12px 10px 6px">${trendsvg(TRENDC.rows,1000,300,TRENDC.target,TRENDC.target2)}</div><div class="bnote">${TRENDC.note}</div>`}
function sparkBlock(nm){if(typeof TRENDA==='undefined'||!TRENDA||!TRENDA[nm])return '';
 const tg=(typeof TRENDC!=='undefined'&&TRENDC&&TRENDC.target)?TRENDC.target:2,tg2=(typeof TRENDC!=='undefined'&&TRENDC)?TRENDC.target2:null;
 const lab=tg2?`紅線＝${(TRENDC.tlab||'門檻')} ${tg.toFixed(2)}・虛線＝BE ${tg2.toFixed(2)}`:`紅虛線＝${tg.toFixed(2)}`;
 return `<h4>近 14 日趨勢 · 柱＝日花費 · 線＝日 ROAS（${lab}）</h4><div style="background:var(--card);border:1px solid var(--line);border-radius:12px;padding:8px 6px 2px">${trendsvg(TRENDA[nm],392,150,tg,tg2)}</div>`}
function scoreBlock(v){if(v.hs===undefined)return '';
 const rows=[["Hook 分（3秒率）",v.hs],["續看分（中段留存）",v.ws],["收單分（購買÷點擊）",v.cs]];
 return `<h4>Video Scores · 帳號內相對分數（0–100）</h4>`+rows.map(r=>`<div class="hrow hrow2"><span class="hl">${r[0]}</span><span class="hbar"><i style="width:${Math.max(2,r[1])}%;background:${r[1]>=67?'var(--green)':r[1]>=34?'var(--gold)':'var(--red)'}"></i></span><span class="hv"><b>${r[1]}</b></span></div>`).join('')+`<div class="xnote">相對分數＝本批 6 支影片內 min–max 正規化；樣本小，看相對強弱、別當絕對評級。</div>`}
let fAv="all",fC="all";
function filters(){$('#filters').innerHTML=LIBAVS.map(a=>`<span class="chip ${fAv===a[0]?'on':''}" data-av="${a[0]}">${a[1]}</span>`).join('')+'<span class="spacer"></span>'+LIBCS.map(c=>`<span class="chip ${fC===c[0]?'on':''}" data-c="${c[0]}">${c[1]}</span>`).join('');
 $('#filters').querySelectorAll('[data-av]').forEach(e=>e.onclick=()=>{fAv=e.dataset.av;render()});
 $('#filters').querySelectorAll('[data-c]').forEach(e=>e.onclick=()=>{fC=e.dataset.c;render()})}
function shown(){return ADS.filter(a=>(fAv==='all'||a.av===fAv)&&(fC==='all'||a.c===fC))}
function grid(){$('#grid').innerHTML=shown().map(a=>{const p=a.perf;const vbg=p?(p.stc==='g'?'var(--green)':'var(--gold)'):'#8a8174';
 const pend=p?`<div class="pend"><span class="pd" style="background:${p.stc==='g'?'var(--green)':'var(--gold)'}"></span>NT$${p.sp.toLocaleString()} · ${p.im.toLocaleString()}曝光 · CTR ${p.ctr}% · ${p.pu}購買</div>`:`<div class="pend"><span class="pd"></span>績效待回填（投放後）</div>`;
 return `<div class="card" data-i="${ADS.indexOf(a)}"><div class="thumb"><img src="${a.file}" loading="lazy"><div class="tags"><span class="tag">${a.avn}</span><span class="tag">${a.vn}</span></div><span class="ver" style="background:${vbg}">${p?p.st:'待投放'}</span></div><div class="body"><div class="hl">${a.hl}</div><div class="angle">${a.cn} · ${a.angle}</div>${pend}</div></div>`}).join('');
 $('#grid').querySelectorAll('.card').forEach(e=>e.onclick=()=>openD(+e.dataset.i))}
function openD(i){const a=ADS[i];const p=a.perf;
 const cells=p?[["花費","NT$"+p.sp.toLocaleString()],["曝光",p.im.toLocaleString()],["CTR",p.ctr+"%"],["購買",p.pu],["ROAS",p.pu>0?(p.roas||"—"):"—(0購)"],["狀態",p.st]]:[["ROAS","—"],["CTR","—"],["Hook Rate","—"],["CPA","—"],["花費","—"],["訂單","—"]];
 const foot=p?`${p.note?`⚠️ ${p.note}<br>`:''}${TEXTS.lib_range} · 檔名 ${a.fname}`:`績效投放後由 Meta Ads 回填 · 檔名 ${a.fname}`;
 $('#drawer').innerHTML=`<button class="x" onclick="closeD()">×</button><img class="dimg" src="${a.file}"><div class="dbody"><span class="ver" style="position:static;display:inline-block;background:${p?(p.stc==='g'?'var(--green)':'var(--gold)'):'#8a8174'}">${p?p.st:'待投放'}</span><h3 style="font-size:22px;font-weight:600;margin:12px 0 2px" class="serif">${a.hl}</h3><div style="color:var(--ink2);font-size:13px">${a.avn} · ${a.cn} · ${a.vn}</div><div style="font-size:13px;margin-top:6px">角度：${a.angle}</div><div class="mgrid">${cells.map(m=>`<div class="mcell"><div class="ml">${m[0]}</div><div class="mv">${m[1]}</div></div>`).join('')}</div><div style="font-size:12px;color:var(--ink2);line-height:1.7">${foot}</div></div>`;
 $('#scrim').classList.add('on');$('#drawer').classList.add('on')}
function closeD(){$('#scrim').classList.remove('on');$('#drawer').classList.remove('on')}
function baseline(){const rows=BASE.rows.map((b,i)=>{return `<tr><td class="rk">${i+1}</td><td>${b[0]}${b[6]==='live'?' <span class="livedot">投放中</span>':''}</td><td class="num roas ${roascls(b[2])}">${b[2].toFixed(2)}</td><td class="num">${b[4]?'NT$'+b[4].toLocaleString():'—'}</td><td class="num">${b[3]}</td><td class="num">NT$${b[1].toLocaleString()}</td><td class="num">${b[5].toFixed(2)}%</td></tr>`}).join('');
 const s=BASE.sum;const sum=`<tr class="sum"><td></td><td>${s[0]}</td><td class="num roas ${roascls(s[1])}">${s[1].toFixed(2)}</td><td class="num">${s[2]?'NT$'+s[2].toLocaleString():'—'}</td><td class="num">${s[3]}</td><td class="num">NT$${s[4].toLocaleString()}</td><td class="num">—</td></tr>`;
 $('#baseline').innerHTML=`<div class="tscroll"><table class="btbl"><thead><tr><th>#</th><th>活動</th><th>ROAS</th><th>CPA</th><th>購買</th><th>花費</th><th>CTR</th></tr></thead><tbody>${rows}${sum}</tbody></table></div><div class="bnote">${BASE.note}</div>`}
function leader(){const rows=LEADER.rows.map(a=>`<tr><td class="rk">${a[0]}</td><td>${a[1]} <span class="itag ${a[8]}" style="padding:2px 8px;font-size:11px">${a[7]}</span><div style="font-size:11px;color:var(--ink2)">${a[2]}</div></td><td class="num roas ${roascls(a[3])}">${a[3]}</td><td class="num">${a[4]}</td><td class="num">${a[5]}</td><td class="num">${a[6]}</td></tr>`).join('');
 $('#leader').innerHTML=`<div class="tscroll"><table class="btbl"><thead><tr><th>#</th><th>廣告</th><th>ROAS</th><th>CPA</th><th>購買</th><th>花費</th></tr></thead><tbody>${rows}</tbody></table></div><div class="bnote">${LEADER.note}</div>`}
function iter(){$('#iter').innerHTML='<div class="itwrap">'+ITER.map(c=>`<div class="itcol"><span class="itag ${c[1]}">${c[0]}</span><div class="itsub">${c[2]}</div><ul>${c[3].map(x=>`<li>${x}</li>`).join('')}</ul></div>`).join('')+'</div>'}
function insights(){$('#insights').innerHTML='<div class="lgrid">'+INS.map(c=>`<div class="lcard"><div class="t">${c[0]}</div><div class="r" style="color:var(--${c[2]})">${c[1]}</div><div class="d">${c[3]}</div></div>`).join('')+'</div>'}
function tabs(){const bar=document.getElementById('tabbar');if(!bar)return;
 const panes=[...document.querySelectorAll('.tabpane')];if(!panes.length){bar.style.display='none';return}
 bar.innerHTML=panes.map(p=>`<button class="tbtn" data-p="${p.id}">${p.dataset.title}</button>`).join('');
 const go=(id,scroll)=>{panes.forEach(p=>p.classList.toggle('on',p.id===id));
  bar.querySelectorAll('.tbtn').forEach(b=>b.classList.toggle('on',b.dataset.p===id));
  try{history.replaceState(null,'','#'+id)}catch(e){}
  if(scroll)window.scrollTo({top:0})};
 bar.querySelectorAll('.tbtn').forEach(b=>b.onclick=()=>go(b.dataset.p,true));
 const h=location.hash.slice(1);
 go(panes.some(p=>p.id===h)?h:panes[0].id,false)}
$('#scrim').onclick=closeD;
function render(){kpis();banner();delivery();scat();trendc();mkTbl('batchtbl',typeof BATCHTBL!=='undefined'?BATCHTBL:null);mkTbl('vtbl',typeof VTBL!=='undefined'?VTBL:null);mkTbl('stbl',typeof STBL!=='undefined'?STBL:null);mkTbl('archsum',typeof ARCHSUM!=='undefined'?ARCHSUM:null);mkTbl('archtbl',typeof ARCHTBL!=='undefined'?ARCHTBL:null);xray();vids();filters();grid();baseline();leader();iter();insights();tabs()} render();
"""

FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23241f19'/%3E%3Ctext x='32' y='45' font-size='38' text-anchor='middle' fill='%23E89A12' font-family='Georgia,serif'%3ES%3C/text%3E%3C/svg%3E"

def render(C):
    def _sec(h2, big): return '<div class="sec"><h2>' + h2 + '</h2><div class="big serif">' + big + '</div></div>'
    deliv_sec = (_sec(C['deliv_h2'], C['deliv_big']) + '\n <div id="delivery"></div>') if C.get('deliv') else ''
    vids_sec = (_sec(C.get('vids_h2', 'Video X-ray · 影片素材解剖'), C.get('vids_big', '')) + '\n <div class="xgrid" id="vids"></div>' + ('\n <div id="vtbl"></div>' if C.get('vtbl') else '')) if C.get('vids') else ''
    scat_sec = (_sec('Creative Tests · 測試散點圖', C.get('scat_big', '')) + '\n <div class="scatwrap" id="scat"></div>' + ('\n <div id="batchtbl"></div>' if C.get('batchtbl') else '')) if C.get('scat') else ''
    trend_sec = (_sec('Account Trend · 帳號日趨勢', C.get('trendc_big', '')) + '\n <div id="trendc"></div>') if (C.get('trendc') or {}).get('rows') else ''
    xray_sec = (_sec(C.get('xray_h2', 'Campaign X-ray · 現役活動全解剖'), C['xray_big']) + '\n <div class="xgrid" id="xray"></div>' + ('\n <div id="stbl"></div>' if C.get('stbl') else '')) if C.get('xray') else ''
    arch_sec = ''
    if C.get('arch_cards') or C.get('archtbl') or C.get('archsum'):
        arch_sec = (_sec(C.get('arch_h2', 'Closed Archive · 已關封存'), C.get('arch_big', ''))
                    + ('\n <div id="archsum"></div>' if C.get('archsum') else '')
                    + ('\n <div class="xgrid" id="xarch"></div>' if C.get('arch_cards') else '')
                    + ('\n <div id="archtbl"></div>' if C.get('archtbl') else ''))
    ov_sec = ('<div id="livebanner"></div>' + trend_sec
              + '\n <div class="sec"><h2>Leaderboard 現役績效排行</h2><div class="big serif">' + C['leader_big'] + '</div></div>\n <div id="leader"></div>'
              + '\n <div class="sec"><h2>Insights 關鍵洞察</h2><div class="big serif">' + C['ins_big'] + '</div></div>\n <div id="insights"></div>'
              + '\n <div class="sec"><h2>Iteration Board 迭代決策</h2><div class="big serif">下一輪怎麼動</div></div>\n <div id="iter"></div>')
    lib_sec = ('<div class="sec"><h2>Creative Library 創意庫</h2><div class="big serif">' + C['lib_big'] + '</div></div>'
               + '\n <div class="controls" id="filters"></div>\n <div class="grid" id="grid"></div>')
    base_sec = ('<div class="sec"><h2>Baseline 起跑線 · 舊批真實成效（已關閉 · 僅參考）</h2><div class="big serif">' + C['base_big'] + '</div></div>\n <div id="baseline"></div>')
    panes = [("p-ov", "總覽", ov_sec)]
    if deliv_sec: panes.append(("p-deliv", "批次投遞", deliv_sec))
    if scat_sec: panes.append(("p-test", "測試分析", scat_sec))
    if vids_sec: panes.append(("p-vid", "🎬 現役影片", vids_sec))
    if xray_sec: panes.append(("p-static", "🖼️ 現役靜態" if C.get('vids') else "素材解剖", xray_sec))
    if arch_sec:
        panes.append(("p-arch", "📦 已關封存", arch_sec + '\n ' + base_sec))
    else:
        panes.append(("p-arch", "起跑線 · 僅參考", base_sec))
    panes.append(("p-lib", "創意庫", lib_sec))
    panes_html = "".join('<section class="tabpane" id="' + pid + '" data-title="' + t + '">' + h + '</section>' for pid, t, h in panes)
    html = f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{C['title']}</title>
<link rel="icon" href="{FAVICON}">
<style>{CSS}</style></head><body>
<div class="hero" style="background:{C['hero_grad']}"><div class="wrap">
 <div class="brandmark"><a href="index.html">← 客戶總覽</a> &nbsp;·&nbsp; {C.get('brand', 'Ads Dashboard')}</div>
 <h1 class="serif">{C['h1']}</h1>
 <div class="sub">{C['sub']}</div>
 <div class="meta">{C['meta_html']}</div>
 <div class="note"><span class="dot"></span>{C['note_html']}</div>
</div></div>
<div class="wrap">
 <div class="kpis" id="kpis"></div>
 <div class="tabbar" id="tabbar"></div>
 {panes_html}
 <footer>{C['footer_html']}</footer>
</div>
<div class="scrim" id="scrim"></div><div class="drawer" id="drawer"></div>
<script>
const KPIS={json.dumps(C['kpis'],ensure_ascii=False)},BANNER={json.dumps(C['banner'],ensure_ascii=False)},DELIV={json.dumps(C.get('deliv'),ensure_ascii=False)},XRAY={json.dumps(C['xray'],ensure_ascii=False)},LIBAVS={json.dumps(C['lib_avs'],ensure_ascii=False)},LIBCS={json.dumps(C['lib_cs'],ensure_ascii=False)},ADS={json.dumps(C['lib_ads'],ensure_ascii=False)},BASE={json.dumps(C['base'],ensure_ascii=False)},LEADER={json.dumps(C['leader'],ensure_ascii=False)},ITER={json.dumps(C['iter'],ensure_ascii=False)},INS={json.dumps(C['ins'],ensure_ascii=False)},TEXTS={json.dumps(C['texts'],ensure_ascii=False)},VIDS={json.dumps(C.get('vids',[]),ensure_ascii=False)},XARCH={json.dumps(C.get('arch_cards',[]),ensure_ascii=False)},VTBL={json.dumps(C.get('vtbl'),ensure_ascii=False)},STBL={json.dumps(C.get('stbl'),ensure_ascii=False)},ARCHTBL={json.dumps(C.get('archtbl'),ensure_ascii=False)},ARCHSUM={json.dumps(C.get('archsum'),ensure_ascii=False)},SCAT={json.dumps(C.get('scat'),ensure_ascii=False)},BATCHTBL={json.dumps(C.get('batchtbl'),ensure_ascii=False)},TRENDC={json.dumps(C.get('trendc'),ensure_ascii=False)},TRENDA={json.dumps(C.get('trenda'),ensure_ascii=False)};
{JS}</script></body></html>"""
    open(C['out'], "w", encoding="utf-8").write(html)
    print("built", C['out'])
