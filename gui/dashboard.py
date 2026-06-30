#!/usr/bin/env python3
"""
Mega Sync Web Dashboard — GUI for your phone's sync folder
Run: python3 dashboard.py
Then open http://localhost:8080 in your phone browser
"""

import http.server
import json
import mimetypes
import os
import subprocess
import urllib.parse
from datetime import datetime

PORT = 8080
SYNC_DIR = os.path.expanduser("~/mega-sync")
REPO_DIR = SYNC_DIR  # same dir, the git repo

# Ensure dirs exist
os.makedirs(SYNC_DIR, exist_ok=True)
os.makedirs(os.path.join(SYNC_DIR, ".git"), exist_ok=True)

def run_cmd(cmd, cwd=REPO_DIR):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)
        return {"ok": r.returncode == 0, "stdout": r.stdout.strip(), "stderr": r.stderr.strip()}
    except Exception as e:
        return {"ok": False, "stdout": "", "stderr": str(e)}

def get_files():
    files = []
    if not os.path.isdir(SYNC_DIR):
        return files
    for f in sorted(os.listdir(SYNC_DIR)):
        fp = os.path.join(SYNC_DIR, f)
        if f.startswith(".") or f == "gui":
            continue
        if os.path.isfile(fp):
            size = os.path.getsize(fp)
            mtime = datetime.fromtimestamp(os.path.getmtime(fp)).isoformat()
            files.append({"name": f, "size": size, "modified": mtime, "path": f})
    return files

def get_status():
    status = run_cmd(["git", "status", "--porcelain"])
    log = run_cmd(["git", "log", "--oneline", "-5"])
    return {
        "files": get_files(),
        "pending": [l for l in status["stdout"].split("\n") if l.strip()],
        "last_commits": [l for l in log["stdout"].split("\n") if l.strip()],
        "repo": "mega-phone-sync",
        "ok": status["ok"] and log["ok"]
    }

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>📁 Mega Sync</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0f0f23;color:#e0e0e0;min-height:100vh}
.container{max-width:800px;margin:0 auto;padding:20px}
h1{font-size:24px;margin:20px 0;display:flex;align-items:center;gap:10px}
h1 span{background:#2d2d5e;padding:2px 10px;border-radius:6px;font-size:12px;color:#888}
.status-bar{background:#1a1a3e;border-radius:12px;padding:16px;margin:16px 0;display:flex;gap:20px;flex-wrap:wrap}
.status-item{flex:1;min-width:120px}
.status-item label{font-size:11px;color:#666;text-transform:uppercase;letter-spacing:1px}
.status-item .value{font-size:20px;font-weight:600;margin-top:4px}
.pending-changes{background:#2d1b1b;border:1px solid #5e2d2d;border-radius:12px;padding:16px;margin:16px 0}
.pending-changes.ok{background:#1b2d1b;border-color:#2d5e2d}
.pending-changes h3{font-size:14px;margin-bottom:8px}
.pending-changes pre{font-size:12px;color:#aaa;white-space:pre-wrap}
.btn{background:#4a4aff;color:white;border:none;padding:12px 24px;border-radius:8px;font-size:15px;cursor:pointer;font-weight:600;transition:.2s}
.btn:hover{background:#5e5eff;transform:translateY(-1px)}
.btn:disabled{opacity:.5;cursor:not-allowed;transform:none}
.btn.secondary{background:#2d2d5e}
.btn.secondary:hover{background:#3d3d7e}
.btn.green{background:#2a6b2a}
.btn.green:hover{background:#3a7b3a}
.btn.red{background:#6b2a2a}
.btn.red:hover{background:#7b3a3a}
.actions{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0}
.upload-zone{border:2px dashed #3d3d6e;border-radius:12px;padding:40px;text-align:center;margin:16px 0;transition:.3s;cursor:pointer}
.upload-zone.dragover{border-color:#4a4aff;background:#1a1a3e}
.upload-zone p{color:#666;font-size:14px}
.upload-zone .big{font-size:40px;margin-bottom:10px}
.file-list{background:#1a1a3e;border-radius:12px;overflow:hidden;margin:16px 0}
.file-list .header{display:flex;padding:12px 16px;font-size:11px;color:#666;text-transform:uppercase;letter-spacing:1px;border-bottom:1px solid #2d2d5e}
.file-item{display:flex;padding:12px 16px;border-bottom:1px solid #2d2d5e;align-items:center;transition:.2s}
.file-item:hover{background:#222252}
.file-item .name{flex:1;font-size:14px}
.file-item .size{color:#666;font-size:12px;width:80px;text-align:right}
.file-item .date{color:#666;font-size:12px;width:160px;text-align:right}
.empty-state{text-align:center;padding:40px;color:#555}
.empty-state .big{font-size:50px;margin-bottom:10px}
.toast{position:fixed;bottom:30px;left:50%;transform:translateX(-50%);background:#1a1a3e;border:1px solid #4a4aff;padding:12px 24px;border-radius:8px;font-size:14px;z-index:999;animation:fadeIn .3s;display:none}
@keyframes fadeIn{from{opacity:0;transform:translateX(-50%) translateY(20px)}}
.spinner{display:inline-block;width:16px;height:16px;border:2px solid #555;border-top-color:#4a4aff;border-radius:50%;animation:spin .6s linear infinite;vertical-align:middle;margin-right:8px}
@keyframes spin{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="container">
  <h1>📁 Mega Sync <span id="statusDot">●</span></h1>

  <div class="status-bar">
    <div class="status-item"><label>Files</label><div class="value" id="fileCount">-</div></div>
    <div class="status-item"><label>Pending</label><div class="value" id="pendingCount">-</div></div>
    <div class="status-item"><label>Last Commit</label><div class="value" id="lastCommit" style="font-size:14px">-</div></div>
  </div>

  <div id="pendingBox" class="pending-changes ok" style="display:none">
    <h3 id="pendingTitle">✅ No pending changes</h3>
    <pre id="pendingDetail"></pre>
  </div>

  <div class="actions">
    <button class="btn green" onclick="syncNow()" id="btnPush">📤 Sync to Mega</button>
    <button class="btn" onclick="pullNow()" id="btnPull">📥 Pull from Mega</button>
    <button class="btn secondary" onclick="refresh()">🔄 Refresh</button>
  </div>

  <div class="upload-zone" id="uploadZone" onclick="document.getElementById('fileInput').click()">
    <div class="big">📄</div>
    <p><strong>Tap to upload</strong> files to sync folder</p>
    <p style="margin-top:8px;font-size:12px">or drag & drop them here</p>
  </div>
  <input type="file" id="fileInput" multiple style="display:none" onchange="uploadFiles(this.files)">

  <div class="file-list" id="fileList">
    <div class="header"><span class="name">Name</span><span class="size">Size</span><span class="date">Modified</span></div>
    <div class="empty-state" id="emptyState">
      <div class="big">📂</div>
      <p>No files yet — upload something!</p>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
async function api(path, method='GET', body=null) {
  const opts = {method};
  if (body instanceof FormData) opts.body = body;
  else if (body) { opts.body = JSON.stringify(body); opts.headers = {'Content-Type':'application/json'}; }
  const r = await fetch(path, opts);
  return r.json();
}

function toast(msg, ok=true) {
  const t = document.getElementById('toast');
  t.textContent = (ok ? '✅ ' : '❌ ') + msg;
  t.style.display = 'block';
  t.style.borderColor = ok ? '#2a6b2a' : '#6b2a2a';
  setTimeout(() => t.style.display = 'none', 3000);
}

function sizeStr(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1048576) return (bytes/1024).toFixed(1) + ' KB';
  return (bytes/1048576).toFixed(1) + ' MB';
}

function dateStr(iso) {
  const d = new Date(iso + 'Z');
  return d.toLocaleString();
}

async function refresh() {
  try {
    const data = await api('/api/status');
    const dot = document.getElementById('statusDot');
    dot.style.color = data.ok ? '#4a4' : '#a44';

    document.getElementById('fileCount').textContent = data.files.length;
    document.getElementById('pendingCount').textContent = data.pending.length;
    document.getElementById('lastCommit').textContent = data.last_commits[0]?.split(' ',1)[0] || '-';

    const pb = document.getElementById('pendingBox');
    const pt = document.getElementById('pendingTitle');
    const pd = document.getElementById('pendingDetail');
    if (data.pending.length > 0) {
      pb.style.display = 'block';
      pb.className = 'pending-changes';
      pt.textContent = '⏳ ' + data.pending.length + ' pending change(s) — sync to Mega';
      pd.textContent = data.pending.join('\\n');
    } else {
      pb.style.display = 'block';
      pb.className = 'pending-changes ok';
      pt.textContent = '✅ No pending changes';
      pd.textContent = '';
    }

    const fl = document.getElementById('fileList');
    const es = document.getElementById('emptyState');
    // Remove existing items (keep header, keep emptyState)
    fl.querySelectorAll('.file-item').forEach(e => e.remove());

    if (data.files.length === 0) {
      es.style.display = 'block';
    } else {
      es.style.display = 'none';
      data.files.forEach(f => {
        const div = document.createElement('div');
        div.className = 'file-item';
        div.innerHTML = '<span class="name">📄 ' + f.name + '</span>' +
          '<span class="size">' + sizeStr(f.size) + '</span>' +
          '<span class="date">' + dateStr(f.modified) + '</span>';
        fl.appendChild(div);
      });
    }
  } catch(e) {
    toast('Failed to load status: ' + e.message, false);
  }
}

async function syncNow() {
  const btn = document.getElementById('btnPush');
  btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>Syncing...';
  try {
    const data = await api('/api/sync', 'POST');
    toast(data.stdout || data.stderr || 'Sync complete!', data.ok);
  } catch(e) { toast('Sync failed: ' + e.message, false); }
  btn.disabled = false; btn.innerHTML = '📤 Sync to Mega';
  refresh();
}

async function pullNow() {
  const btn = document.getElementById('btnPull');
  btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>Pulling...';
  try {
    const data = await api('/api/pull', 'POST');
    toast(data.stdout || data.stderr || 'Pull complete!', data.ok);
  } catch(e) { toast('Pull failed: ' + e.message, false); }
  btn.disabled = false; btn.innerHTML = '📥 Pull from Mega';
  refresh();
}

async function uploadFiles(files) {
  if (!files.length) return;
  const fd = new FormData();
  for (const f of files) fd.append('files', f);
  const btn = document.getElementById('uploadZone');
  btn.innerHTML = '<span class="spinner"></span> Uploading...';
  try {
    const data = await api('/api/upload', 'POST', fd);
    toast('Uploaded ' + files.length + ' file(s)!', data.ok);
  } catch(e) { toast('Upload failed: ' + e.message, false); }
  document.getElementById('fileInput').value = '';
  btn.innerHTML = '<div class="big">📄</div><p><strong>Tap to upload</strong> files to sync folder</p><p style="margin-top:8px;font-size:12px">or drag & drop them here</p>';
  refresh();
}

// Drag & drop
const uz = document.getElementById('uploadZone');
uz.addEventListener('dragover', e => { e.preventDefault(); uz.classList.add('dragover'); });
uz.addEventListener('dragleave', () => uz.classList.remove('dragover'));
uz.addEventListener('drop', e => { e.preventDefault(); uz.classList.remove('dragover'); uploadFiles(e.dataTransfer.files); });

refresh();
</script>
</body>
</html>"""

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=os.path.dirname(__file__), **kw)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/status":
            self._json(get_status())
        elif parsed.path == "/":
            self._html(HTML)
        elif parsed.path.startswith("/files/"):
            # serve uploaded files
            fname = urllib.parse.unquote(parsed.path[7:])
            fpath = os.path.join(SYNC_DIR, fname)
            if os.path.isfile(fpath):
                self.send_response(200)
                self.send_header("Content-Type", mimetypes.guess_type(fname)[0] or "application/octet-stream")
                self.send_header("Content-Disposition", f'inline; filename="{fname}"')
                self.end_headers()
                with open(fpath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/sync":
            r = run_cmd(["bash", "./mega-tool.sh", "push"], cwd=SYNC_DIR)
            self._json(r)
        elif self.path == "/api/pull":
            r = run_cmd(["bash", "./mega-tool.sh", "pull"], cwd=SYNC_DIR)
            self._json(r)
        elif self.path == "/api/upload":
            ct = self.headers.get("Content-Type", "")
            if "multipart/form-data" not in ct:
                self._json({"ok": False, "stdout": "", "stderr": "Expected multipart upload"})
                return
            import cgi
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={"REQUEST_METHOD": "POST"})
            items = form.getlist("files")
            ok = True
            for item in items:
                if item.file and item.filename:
                    fname = os.path.basename(item.filename)
                    fpath = os.path.join(SYNC_DIR, fname)
                    with open(fpath, "wb") as f:
                        f.write(item.file.read())
            self._json({"ok": True, "stdout": f"Uploaded {len(items)} file(s)", "stderr": ""})
        else:
            self.send_error(404)

    def _json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _html(self, html):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, f, *a):
        pass  # quieter

if __name__ == "__main__":
    print(f"")
    print(f"  📁 Mega Sync Dashboard")
    print(f"  ─────────────────────")
    print(f"  Open in your phone browser:")
    print(f"  🌐 http://localhost:{PORT}")
    print(f"  🌐 http://127.0.0.1:{PORT}")
    print(f"")
    print(f"  Your sync folder: ~/mega-sync/")
    print(f"  Drop files in the folder or upload via the web UI.")
    print(f"  Press Ctrl+C to stop.")
    print(f"")
    srv = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        srv.server_close()
