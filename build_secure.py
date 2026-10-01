#!/usr/bin/env python3
# 廣告績效檢視台 — 加密發布版（Netlify 等公開主機用）。
# 把 總覽＋各客戶頁 合成完整單檔，再以 AES-256-GCM（PBKDF2-SHA256 310k 迭代）整包加密：
# 主機上只存密文；開頁先輸入密碼，答對才在瀏覽器內解密渲染。密碼從環境變數 DASH_PASSWORD 讀，不寫進程式。
# 登入狀態保持：解鎖後把「解密金鑰」（非密碼）存 localStorage，SESSION_HOURS 內重新整理自動解鎖、每次解鎖續期。
# 鹽值固定存 deploy-secure/salt.json（跨部署不變→重新部署不用重新登入）；換密碼時刪掉 salt.json 一起重生也可。
# 跑法：python3 build_all.py → python3 build_artifact.py（產 shell 素材）→ python3 build_secure.py
import base64, os, json, secrets
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

D = os.path.dirname(os.path.abspath(__file__))
OUTDIR = f"{D}/deploy-secure"
PASSWORD = os.environ.get("DASH_PASSWORD", "")   # 換密碼時建議連 salt.json 一併刪除重生
if len(PASSWORD) < 12:
    raise SystemExit("請先設定 DASH_PASSWORD 環境變數（至少 12 個字），例如：DASH_PASSWORD='…' python3 build_secure.py")
BRAND = os.environ.get("DASH_BRAND", "Demo Agency")
ITER = 310_000
SESSION_HOURS = 12      # ← 登入狀態保持時數（每次成功解鎖自動續期）

os.makedirs(OUTDIR, exist_ok=True)

# 0) 固定鹽值（跨部署不變，讓瀏覽器快取的金鑰在重新部署後仍有效）
SALT_FILE = f"{OUTDIR}/salt.json"
if os.path.exists(SALT_FILE):
    salt = base64.b64decode(json.load(open(SALT_FILE))["salt"])
else:
    salt = secrets.token_bytes(16)
    json.dump({"salt": base64.b64encode(salt).decode()}, open(SALT_FILE, "w"))

# 1) 內容＝與 Artifact 版相同的 shell，但補成完整 HTML 文件
FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23241f19'/%3E%3Ctext x='32' y='45' font-size='38' text-anchor='middle' fill='%23E89A12' font-family='Georgia,serif'%3ES%3C/text%3E%3C/svg%3E"
frag = open(f"{D}/platform-artifact.html", encoding="utf-8").read()
inner = f"<!doctype html><html lang=\"zh-Hant\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><link rel=\"icon\" href=\"{FAVICON}\"></head><body style=\"margin:0\">{frag}</body></html>"

# 2) 加密（nonce 每次重生；同 key 不同 nonce 安全）
nonce = secrets.token_bytes(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(PASSWORD.encode())
ct = AESGCM(key).encrypt(nonce, inner.encode("utf-8"), None)
payload = dict(salt=base64.b64encode(salt).decode(), nonce=base64.b64encode(nonce).decode(),
               it=ITER, data=base64.b64encode(ct).decode())

# 3) 登入殼（沿用檢視台視覺語言＋自動解鎖）
GATE = f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{BRAND} · 廣告績效檢視台</title>
<link rel="icon" href="{FAVICON}">
<style>
:root{{--paper:#F2EEE8;--ink:#241f19;--ink2:#6b6155;--line:#ddd3c4;--card:#FFFCF6;--gold:#E89A12;--red:#D6283A}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{min-height:100vh;display:flex;align-items:center;justify-content:center;background:var(--paper);font-family:"PingFang TC","Noto Sans TC",system-ui,sans-serif;color:var(--ink)}}
.gate{{width:min(400px,92vw);background:var(--card);border:1px solid var(--line);border-radius:20px;box-shadow:0 14px 44px rgba(50,40,25,.16);overflow:hidden}}
.band{{height:9px;background:linear-gradient(90deg,#b81f2e,#e0911b 50%,#7c2f6e)}}
.in{{padding:30px 30px 32px}}
.bm{{font-size:11px;letter-spacing:.36em;text-transform:uppercase;color:var(--ink2);font-weight:600}}
h1{{font-family:"Songti TC",Georgia,serif;font-size:26px;font-weight:600;margin:8px 0 2px}}
.sub{{font-size:12.5px;color:var(--ink2);margin-bottom:20px}}
.pwrap{{position:relative}}
input{{width:100%;padding:12px 46px 12px 14px;border:1px solid var(--line);border-radius:12px;font-size:15px;background:#fff;font-family:inherit}}
input:focus{{outline:2px solid var(--gold);border-color:var(--gold)}}
#eye{{position:absolute;right:4px;top:50%;transform:translateY(-50%);width:38px;margin:0;padding:8px;background:none;border:none;color:var(--ink2);cursor:pointer;display:flex;align-items:center;justify-content:center}}
#eye:hover{{color:var(--ink)}}
#eye svg{{width:20px;height:20px}}
button{{width:100%;margin-top:12px;padding:12px;border:none;border-radius:12px;background:var(--ink);color:#fff;font-size:14.5px;font-weight:600;cursor:pointer;font-family:inherit}}
button:disabled{{opacity:.55;cursor:wait}}
.err{{color:var(--red);font-size:12.5px;margin-top:10px;min-height:18px}}
.ft{{font-size:11px;color:var(--ink2);margin-top:16px;line-height:1.7}}
</style></head><body>
<form class="gate" id="f">
 <div class="band"></div>
 <div class="in">
  <div class="bm">{BRAND}</div>
  <h1>廣告績效檢視台</h1>
  <div class="sub">內部數據平台 · 內容已整包加密，請輸入通行碼</div>
  <div class="pwrap">
   <input id="pw" type="password" placeholder="通行碼" autocomplete="current-password" autofocus>
   <button type="button" id="eye" aria-label="顯示/隱藏通行碼" title="顯示/隱藏通行碼">
    <svg id="eyeOpen" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
    <svg id="eyeOff" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
   </button>
  </div>
  <button id="btn" type="submit">解鎖</button>
  <div class="err" id="err"></div>
  <div class="ft">頁面在你的瀏覽器內解密，密碼不會被傳送到任何伺服器。解鎖後 {SESSION_HOURS} 小時內重新整理免輸入（金鑰只存在這台裝置）。忘記通行碼請找管理者。</div>
 </div>
</form>
<script>
document.getElementById('eye').onclick=()=>{{
 const pw=document.getElementById('pw'),show=pw.type==='password';
 pw.type=show?'text':'password';
 document.getElementById('eyeOpen').style.display=show?'none':'';
 document.getElementById('eyeOff').style.display=show?'':'none';
 pw.focus();
}};
const P={json.dumps(payload)};
const LS='sa_gate',HOURS={SESSION_HOURS};
const b=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
const b64=a=>{{const u=new Uint8Array(a);let s='';for(let i=0;i<u.length;i++)s+=String.fromCharCode(u[i]);return btoa(s)}};
function remember(rawKey){{try{{localStorage.setItem(LS,JSON.stringify({{k:b64(rawKey),s:P.salt,exp:Date.now()+HOURS*3600e3}}))}}catch(_){{}}}}
async function unlock(key){{  // 解密成功才回傳 html；失敗會 throw
 const pt=await crypto.subtle.decrypt({{name:'AES-GCM',iv:b(P.nonce)}},key,b(P.data));
 return new TextDecoder().decode(pt);
}}
async function show(html){{
 if(document.readyState!=='complete')await new Promise(r=>addEventListener('load',r,{{once:true}}));
 document.open();document.write(html);document.close();
}}
(async()=>{{  // 自動解鎖：金鑰仍有效（未過期＋鹽值未變）就直接進站
 let st=null;try{{st=JSON.parse(localStorage.getItem(LS)||'null')}}catch(_){{}}
 if(!st||st.s!==P.salt||!(st.exp>Date.now())){{try{{localStorage.removeItem(LS)}}catch(_){{}};return}}
 const btn=document.getElementById('btn');btn.disabled=true;btn.textContent='自動解鎖中…';
 try{{
  const raw=b(st.k);
  const key=await crypto.subtle.importKey('raw',raw,{{name:'AES-GCM'}},false,['decrypt']);
  const html=await unlock(key);
  remember(raw.buffer);  // 解密成功才續期
  await show(html);
 }}catch(_){{
  try{{localStorage.removeItem(LS)}}catch(__){{}}
  btn.disabled=false;btn.textContent='解鎖';
 }}
}})();
document.getElementById('f').onsubmit=async e=>{{
 e.preventDefault();
 const btn=document.getElementById('btn'),err=document.getElementById('err');
 btn.disabled=true;btn.textContent='解密中…';err.textContent='';
 try{{
  const km=await crypto.subtle.importKey('raw',new TextEncoder().encode(document.getElementById('pw').value),'PBKDF2',false,['deriveBits']);
  const bits=await crypto.subtle.deriveBits({{name:'PBKDF2',salt:b(P.salt),iterations:P.it,hash:'SHA-256'}},km,256);
  const key=await crypto.subtle.importKey('raw',bits,{{name:'AES-GCM'}},false,['decrypt']);
  const html=await unlock(key);   // 密碼錯會 throw，不會存金鑰
  remember(bits);                  // 解密成功 → 存金鑰（12h 免輸入）
  await show(html);
 }}catch(_){{
  err.textContent='通行碼不正確';btn.disabled=false;btn.textContent='解鎖';
 }}
}};
</script></body></html>"""
out = f"{OUTDIR}/index.html"
open(out, "w", encoding="utf-8").write(GATE)
os.system(f'cd "{OUTDIR}" && rm -f ads-dashboard-secure.zip && zip -q -X ads-dashboard-secure.zip index.html')
print("built", out, f"{os.path.getsize(out)//1024} KB ; zip", os.path.getsize(f"{OUTDIR}/ads-dashboard-secure.zip")//1024, "KB ; session", SESSION_HOURS, "h")
