# keeper.py - ROBBER KEEPER v4 - Bilkul UptimeRobot Jaisa! - By Abhishek Pal
# Jitna chaho utna URL daalo! Delete bhi karo! Sab save rahega!
from flask import Flask, jsonify, render_template_string, request
import requests, threading, time, os, json
from datetime import datetime
from collections import deque

app = Flask(__name__)

FILE = "monitors.json"

# ===== Pehle se 2 daal diye hain - Tu chahe to delete kar sakta hai! =====
def load_monitors():
    if os.path.exists(FILE):
        try:
            with open(FILE) as f:
                return json.load(f)
        except:
            pass
    return [
        {"id": "1", "name": "ROBBER ENGINE", "url": "https://robber-v2.onrender.com", "every": 60, "success": 0, "fail": 0, "last_status": "Wait...", "last_ping": "-", "awake": True},
        {"id": "2", "name": "ROBBER KEEPER - KHUD", "url": "https://robber-keeper-1.onrender.com", "every": 10, "success": 0, "fail": 0, "last_status": "Wait...", "last_ping": "-", "awake": True},
    ]

def save_monitors():
    try:
        with open(FILE, "w") as f:
            json.dump(monitors, f)
    except Exception as e:
        print("Save fail:", e)

monitors = load_monitors()
logs = deque(maxlen=100)
lock = threading.Lock()

def ping_one(m):
    try:
        start = time.time()
        # UptimeRobot jaisa - seedha URL pe ping!
        r = requests.get(m["url"], timeout=10)
        ms = int((time.time() - start) * 1000)
        with lock:
            if r.status_code == 200:
                m["success"] += 1
                m["awake"] = True
                m["last_status"] = f"UP ✅ - {ms}ms"
                logs.appendleft({"time": str(datetime.now())[:19], "name": m["name"], "status": "✅ UP", "ms": ms})
            else:
                m["fail"] += 1
                m["awake"] = False
                m["last_status"] = f"DOWN 😴 - {r.status_code}"
                logs.appendleft({"time": str(datetime.now())[:19], "name": m["name"], "status": "😴 DOWN", "ms": ms})
            m["last_ping"] = str(datetime.now())[:19]
            save_monitors()
        print(f"{'✅' if m['awake'] else '😴'} {m['name']} - {m['last_status']}")
    except Exception as e:
        with lock:
            m["fail"] += 1
            m["awake"] = False
            m["last_status"] = f"DOWN ❌"
            m["last_ping"] = str(datetime.now())[:19]
            logs.appendleft({"time": str(datetime.now())[:19], "name": m["name"], "status": "❌ DOWN", "ms": 0})
            save_monitors()
        print(f"❌ {m['name']} DOWN - {e}")

def monitor_loop(m):
    time.sleep(2)
    while True:
        # Agar delete ho gaya to ruk jao!
        if m not in monitors:
            break
        ping_one(m)
        time.sleep(m["every"])

for m in monitors:
    threading.Thread(target=monitor_loop, args=(m,), daemon=True).start()

HTML = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ROBBER KEEPER - UptimeRobot Jaisa</title>
<style>*{margin:0;padding:0;box-sizing:border-box;font-family:Arial}body{background:#0f172a;color:#fff;padding:14px;max-width:800px;margin:auto}
.top{background:#1e293b;padding:16px;border-radius:14px;display:flex;justify-content:space-between;align-items:center}
.top h1{font-size:22px}.top h1 span{color:#FF6B00}.top p{font-size:12px;color:#94a3b8}
.addbox{background:#1e293b;padding:16px;border-radius:14px;margin-top:12px;border:2px dashed #FF6B00}
.addbox h3{color:#FF6B00}
input,select{width:100%;padding:13px;margin-top:10px;background:#0f172a;color:#fff;border:1px solid #334155;border-radius:10px;font-size:14px}
.addbtn{width:100%;padding:14px;background:#22c55e;color:#fff;border:none;border-radius:12px;font-weight:900;font-size:16px;margin-top:12px;cursor:pointer}
.monitor{background:#1e293b;padding:14px;border-radius:12px;margin-top:10px;display:flex;justify-content:space-between;align-items:center;gap:10px}
.dot{width:14px;height:14px;border-radius:50%;flex-shrink:0}.green{background:#22c55e;box-shadow:0 0 10px #22c55e}.red{background:#ef4444;box-shadow:0 0 10px #ef4444}
.minfo{flex:1;min-width:0}.minfo b{font-size:15px;word-break:break-word}.minfo p{font-size:12px;color:#94a3b8;word-break:break-all;margin-top:3px}.minfo small{font-size:11px;color:#cbd5e1}
.delbtn{background:#ef4444;color:#fff;border:none;padding:8px 10px;border-radius:8px;cursor:pointer;font-size:12px}
.pingbtn{background:#334155;color:#fff;border:none;padding:8px 10px;border-radius:8px;cursor:pointer;font-size:12px;margin-top:5px}
table{width:100%;border-collapse:collapse;margin-top:12px;font-size:12px}th,td{padding:9px;text-align:left;border-bottom:1px solid #334155}
</style></head><body>
<div class="top"><div><h1>ROBBER <span>KEEPER</span> 🤖</h1><p>UptimeRobot Jaisa - Apna Wala • By Abhishek Pal</p></div><div style="text-align:right;"><b id="upCount" style="color:#22c55e;font-size:20px;">0 UP</b><br><small id="downCount" style="color:#ef4444;">0 DOWN</small></div></div>

<div class="addbox">
<h3>➕ Naya Website Add Karo - Jitna Chaho Utna!</h3>
<input id="mName" placeholder="Naam kya rakhu? - Jaise ROBBER ADMIN">
<input id="mUrl" placeholder="URL daalo - Jaise https://robber-v2.onrender.com">
<select id="mEvery">
<option value="10">Har 10 Sec Me Check Karo - Keeper Ke Liye</option>
<option value="60" selected>Har 1 Min Me Check Karo - Engine Ke Liye</option>
<option value="120">Har 2 Min Me Check Karo</option>
<option value="300">Har 5 Min Me Check Karo - UptimeRobot Jaisa</option>
</select>
<button class="addbtn" onclick="addMonitor()">✅ ADD MONITOR - AB SE YE BHI UTHEGA!</button>
<p style="font-size:11px;color:#94a3b8;text-align:center;margin-top:8px;">Jitna chaho utna add kar sakte ho - Koi limit nahi!</p>
</div>

<h3 style="margin-top:18px;">📡 Mere Monitors - <span id="total">0</span></h3>
<div id="list"><p style="color:#94a3b8;">Loading...</p></div>

<h3 style="margin-top:18px;">📜 Last Ping Ka Hisab</h3>
<table><tr><th>Time</th><th>Naam</th><th>Status</th><th>Speed</th></tr><tbody id="logs"></tbody></table>

<script>
async function load(){
  let r = await fetch("/api/monitors"); let j = await r.json();
  document.getElementById("total").innerText = j.monitors.length;
  let up = j.monitors.filter(m=>m.awake).length;
  document.getElementById("upCount").innerText = up + " UP";
  document.getElementById("downCount").innerText = (j.monitors.length-up) + " DOWN";
  let h = "";
  j.monitors.forEach(m => {
    let total = m.success + m.fail;
    let uptime = total>0 ? Math.round(m.success/total*100) : 100;
    h += `<div class="monitor"><div class="dot ${m.awake?'green':'red'}"></div><div class="minfo"><b>${m.name}</b><p>${m.url}</p><small>${m.last_status} | Last: ${m.last_ping} | Har ${m.every} sec | Uptime: ${uptime}% | ✅ ${m.success} ❌ ${m.fail}</small></div><div><button class="pingbtn" onclick="pingNow('${m.id}')">🔄 PING</button><br><button class="delbtn" onclick="delMonitor('${m.id}')">🗑 DELETE</button></div></div>`;
  });
  document.getElementById("list").innerHTML = h || "<p style='color:#94a3b8;'>Koi monitor nahi - Upar se add karo!</p>";
  let lh=""; j.logs.forEach(l=>{ lh+=`<tr><td>${l.time}</td><td>${l.name}</td><td>${l.status}</td><td>${l.ms}ms</td></tr>`; });
  document.getElementById("logs").innerHTML = lh || "<tr><td colspan=4>Abhi koi ping nahi...</td></tr>";
}
async function addMonitor(){
  let name=document.getElementById("mName").value.trim();
  let url=document.getElementById("mUrl").value.trim();
  let every=document.getElementById("mEvery").value;
  if(!name){ alert("Bhaiya Naam to daalo!"); return; }
  if(!url){ alert("Bhaiya URL to daalo!"); return; }
  if(!url.startsWith("http")) url="https://"+url;
  await fetch("/api/add-monitor",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name,url,every:parseInt(every)})});
  document.getElementById("mName").value=""; document.getElementById("mUrl").value="";
  alert("Ho Gaya! "+name+" Add Ho Gaya! Ab Ye Bhi Uthega!");
  load();
}
async function delMonitor(id){ if(!confirm("Delete kar du isko?")) return; await fetch("/api/delete-monitor",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({id})}); load(); }
async function pingNow(id){ await fetch("/api/ping-now",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({id})}); load(); }
load(); setInterval(load,5000);
</script></body></html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/monitors')
def get_monitors():
    return jsonify({"monitors": monitors, "logs": list(logs)})

@app.route('/api/add-monitor', methods=['POST'])
def add_monitor():
    d = request.json
    url = d.get("url","").strip()
    if not url.startswith("http"): url = "https://" + url
    m = {"id": str(int(time.time()*1000)), "name": d.get("name","Monitor"), "url": url, "every": int(d.get("every",60)), "success": 0, "fail": 0, "last_status": "Abhi add hua...", "last_ping": "-", "awake": True}
    monitors.append(m)
    save_monitors()
    threading.Thread(target=monitor_loop, args=(m,), daemon=True).start()
    return jsonify({"ok": True})

@app.route('/api/delete-monitor', methods=['POST'])
def delete_monitor():
    d = request.json
    global monitors
    monitors = [m for m in monitors if m["id"] != d.get("id")]
    save_monitors()
    return jsonify({"ok": True})

@app.route('/api/ping-now', methods=['POST'])
def ping_now():
    d = request.json
    for m in monitors:
        if m["id"] == d.get("id"):
            ping_one(m)
            break
    return jsonify({"ok": True})

@app.route('/api/self-ping')
def self_ping():
    return jsonify({"ok": True})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
