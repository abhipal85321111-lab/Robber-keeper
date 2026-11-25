# keeper.py - ROBBER KEEPER v2 - By Abhishek Pal - 13 Saal Ka Developer!
# Khud ko har 10 sec me uthayega + Engine ko har 1 min me uthayega!
# Koi nahi soyega!
from flask import Flask, jsonify, render_template_string
import requests, threading, time, os
from datetime import datetime
from collections import deque

app = Flask(__name__)

# ===== 2 URL - Dono Yaha Daal De! =====
# Engine ka URL - Jisko 1 min me uthana hai
ROBBER_URL = os.environ.get("ROBBER_URL", "https://tera-robber.onrender.com")
# Keeper ka khud ka URL - Jisko 10 sec me uthana hai
# Render se Keeper ka URL milne ke baad yaha daal dena!
# Jaise https://robber-keeper.onrender.com
KEEPER_URL = os.environ.get("KEEPER_URL", "https://robber-keeper.onrender.com")

PING_ENGINE_EVERY = 60  # Engine ko har 60 sec = 1 min me!
PING_SELF_EVERY = 10    # Khud ko har 10 sec me!

keeper_logs = deque(maxlen=100)
self_logs = deque(maxlen=50)

keeper_stats = {
    "total_engine_pings": 0, "engine_success": 0, "engine_failed": 0,
    "total_self_pings": 0, "self_success": 0,
    "last_engine_ping": "", "last_engine_status": "",
    "last_self_ping": "", "last_self_status": "",
    "robber_awake": True, "keeper_awake": True,
    "uptime": "100%", "started_at": str(datetime.now())[:19]
}

# ===== ROBOT 1 - ENGINE KO UTHAO - Har 1 Min Me! =====
def ping_engine():
    try:
        start = time.time()
        r = requests.get(ROBBER_URL + "/api/stats", timeout=10)
        ms = int((time.time() - start) * 1000)
        keeper_stats["total_engine_pings"] += 1
        if r.status_code == 200:
            keeper_stats["engine_success"] += 1
            keeper_stats["robber_awake"] = True
            keeper_stats["last_engine_status"] = f"JAAG RAHA HAI ✅ - {ms}ms"
            keeper_logs.appendleft({"time": str(datetime.now())[:19], "target": "ENGINE", "status": "✅ JAAG RAHA", "ms": ms})
            print(f"✅ ENGINE PING OK - {ms}ms - {ROBBER_URL}")
        else:
            keeper_stats["engine_failed"] += 1
            keeper_stats["last_engine_status"] = f"SO RAHA 😴 - {r.status_code}"
            keeper_logs.appendleft({"time": str(datetime.now())[:19], "target": "ENGINE", "status": "😴 SO RAHA", "ms": ms})
            print(f"😴 ENGINE SO RAHA - {r.status_code}")
    except Exception as e:
        keeper_stats["total_engine_pings"] += 1
        keeper_stats["engine_failed"] += 1
        keeper_stats["robber_awake"] = False
        keeper_stats["last_engine_status"] = f"DOWN ❌ - {str(e)[:40]}"
        keeper_logs.appendleft({"time": str(datetime.now())[:19], "target": "ENGINE", "status": "❌ DOWN", "ms": 0})
        print(f"❌ ENGINE DOWN - {e}")
    keeper_stats["last_engine_ping"] = str(datetime.now())[:19]
    total = keeper_stats["total_engine_pings"]
    if total > 0:
        keeper_stats["uptime"] = f"{round(keeper_stats['engine_success']/total*100, 1)}%"

def engine_loop():
    print(f"🚀 ENGINE ROBOT START! Har {PING_ENGINE_EVERY} sec me Engine ko uthayega!")
    time.sleep(5)  # Pehle 5 sec ruko, server chalu hone do
    while True:
        ping_engine()
        time.sleep(PING_ENGINE_EVERY)

# ===== ROBOT 2 - KHUD KO UTHAO - Har 10 Sec Me! =====
def ping_self():
    try:
        start = time.time()
        # Khud ko ping karo - Apne hi /api/self-ping pe!
        # Ye Render ko batayega - "Main kaam kar raha hu, mujhe mat sulao!"
        r = requests.get(KEEPER_URL + "/api/self-ping", timeout=8)
        ms = int((time.time() - start) * 1000)
        keeper_stats["total_self_pings"] += 1
        if r.status_code == 200:
            keeper_stats["self_success"] += 1
            keeper_stats["keeper_awake"] = True
            keeper_stats["last_self_status"] = f"MAIN JAAG RAHA HU ✅ - {ms}ms"
            self_logs.appendleft({"time": str(datetime.now())[:19], "target": "SELF", "status": "✅ JAAG RAHA", "ms": ms})
            print(f"✅ SELF PING OK - Main jaag raha hu! {ms}ms")
        else:
            keeper_stats["last_self_status"] = f"SO RAHA 😴 - {r.status_code}"
            print(f"😴 SELF PING FAIL - {r.status_code}")
    except Exception as e:
        keeper_stats["total_self_pings"] += 1
        keeper_stats["keeper_awake"] = False
        keeper_stats["last_self_status"] = f"ERROR - {str(e)[:40]}"
        print(f"❌ SELF PING ERROR - {e}")
    keeper_stats["last_self_ping"] = str(datetime.now())[:19]

def self_loop():
    print(f"🤖 SELF ROBOT START! Har {PING_SELF_EVERY} sec me khud ko uthayega!")
    time.sleep(3)
    while True:
        ping_self()
        time.sleep(PING_SELF_EVERY)

# Dono Robot ko alag-alag Thread me chalao!
threading.Thread(target=engine_loop, daemon=True).start()
threading.Thread(target=self_loop, daemon=True).start()
print("🔥 DONO ROBOT START HO GAYE! Koi nahi soyega ab!")

# ===== KEEPER DASHBOARD =====
KEEPER_HTML = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ROBBER KEEPER v2 - By Abhishek</title>
<style>*{margin:0;padding:0;box-sizing:border-box;font-family:Arial}body{background:#0f0f12;color:#fff;padding:16px}
.logo{font-size:30px;font-weight:900}.logo span{color:#FF6B00}
.box{padding:18px;border-radius:14px;margin-top:12px;text-align:center}
.green{background:linear-gradient(135deg,#34A853,#0f0f12)}.orange{background:linear-gradient(135deg,#FF6B00,#A855F7)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-top:12px}
.card{background:#1e1e24;padding:16px;border-radius:12px;border:1px solid #333;text-align:center}.card h2{font-size:24px;margin:6px 0}.card small{color:#aaa}
table{width:100%;border-collapse:collapse;margin-top:12px;font-size:12px}th,td{padding:9px;text-align:left;border-bottom:1px solid #333}
button{padding:12px 18px;background:#FF6B00;color:#fff;border:none;border-radius:22px;cursor:pointer;font-weight:bold;margin-top:10px}
</style></head><body>
<div class="logo">ROBBER <span>KEEPER v2</span> 🤖</div>
<p style="color:#aaa;font-size:13px;">By Abhishek Pal • 13 Saal Ka Developer • Khud Ko + Engine Ko Uthata Hai!</p>

<div class="box green"><small>ENGINE - ROBBER</small><h1 id="engineStatus">CHECK...</h1><p id="engineLast">-</p><p style="font-size:12px;color:#ccc;margin-top:4px;">Har 1 Min Me Ping Hota Hai</p></div>
<div class="box orange"><small>KEEPER - KHUD</small><h1 id="selfStatus">CHECK...</h1><p id="selfLast">-</p><p style="font-size:12px;opacity:.8;margin-top:4px;">Har 10 Sec Me Khud Ko Ping Karta Hai</p></div>

<div class="grid">
<div class="card"><small>🚀 ENGINE PING</small><h2 id="eTotal">0</h2><p style="font-size:11px;color:#888;">Success: <span id="eSucc">0</span></p></div>
<div class="card"><small>🤖 SELF PING</small><h2 id="sTotal">0</h2><p style="font-size:11px;color:#888;">Success: <span id="sSucc">0</span></p></div>
<div class="card"><small>📈 UPTIME</small><h2 id="uptime">100%</h2></div>
<div class="card"><small>⏰ STARTED</small><h2 id="started" style="font-size:13px;">-</h2></div>
</div>

<button onclick="pingEngineNow()">🚀 ENGINE KO ABHI UTHAO!</button>
<button onclick="pingSelfNow()" style="background:#333;">🤖 KHUD KO ABHI UTHAO!</button>

<h3 style="margin-top:20px;">📜 Last Ping Ka Hisab - Engine + Self</h3>
<table><tr><th>Time</th><th>Kisko?</th><th>Status</th><th>Speed</th></tr><tbody id="logs"></tbody></table>
<p style="color:#666;font-size:11px;text-align:center;margin-top:16px;">© 2026 Robber Keeper v2 - Samraj Ka Pehla Sipahi!</p>
<script>
async function load(){
  let r = await fetch("/api/keeper-stats"); let j = await r.json();
  document.getElementById("engineStatus").innerText = j.robber_awake ? "ENGINE JAAG RAHA ✅" : "ENGINE SO RAHA 😴";
  document.getElementById("engineLast").innerText = "Last: " + j.last_engine_ping + " | " + j.last_engine_status;
  document.getElementById("selfStatus").innerText = j.keeper_awake ? "MAIN JAAG RAHA ✅" : "MAIN SO RAHA 😴";
  document.getElementById("selfLast").innerText = "Last: " + j.last_self_ping + " | " + j.last_self_status;
  document.getElementById("eTotal").innerText = j.total_engine_pings;
  document.getElementById("eSucc").innerText = j.engine_success;
  document.getElementById("sTotal").innerText = j.total_self_pings;
  document.getElementById("sSucc").innerText = j.self_success;
  document.getElementById("uptime").innerText = j.uptime;
  document.getElementById("started").innerText = j.started_at;
  let h = "";
  let all = [...j.logs, ...j.self_logs].sort((a,b)=> b.time.localeCompare(a.time)).slice(0,30);
  all.forEach(l => { h += `<tr><td>${l.time}</td><td>${l.target}</td><td>${l.status}</td><td>${l.ms}ms</td></tr>`; });
  document.getElementById("logs").innerHTML = h || "<tr><td colspan=4>Abhi koi ping nahi...</td></tr>";
}
async function pingEngineNow(){ await fetch("/api/ping-engine-now", {method:"POST"}); load(); }
async function pingSelfNow(){ await fetch("/api/ping-self-now", {method:"POST"}); load(); }
load(); setInterval(load, 5000);
</script></body></html>
"""

@app.route('/')
def home():
    return render_template_string(KEEPER_HTML)

@app.route('/api/self-ping')
def self_ping():
    # Ye wala endpoint khud ko ping karne ke liye hai - Halka hai!
    return jsonify({"ok": True, "msg": "Main jaag raha hu!", "time": str(datetime.now())[:19]})

@app.route('/api/keeper-stats')
def stats():
    return jsonify({**keeper_stats, "robber_url": ROBBER_URL, "keeper_url": KEEPER_URL, "logs": list(keeper_logs), "self_logs": list(self_logs), "ping_engine_every": PING_ENGINE_EVERY, "ping_self_every": PING_SELF_EVERY})

@app.route('/api/ping-engine-now', methods=['POST'])
def ping_engine_now():
    ping_engine()
    return jsonify({"ok": True, "msg": "Engine ko abhi ping kar diya!"})

@app.route('/api/ping-self-now', methods=['POST'])
def ping_self_now():
    ping_self()
    return jsonify({"ok": True, "msg": "Khud ko abhi ping kar diya!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
