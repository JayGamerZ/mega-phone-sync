#!/usr/bin/env python3
"""
Auto-watcher — watches ~/mega-sync/ and auto-pushes changes to GitHub.
This makes it behave like a Dropbox folder — just drop files in and they sync.

Run: python3 watch-and-sync.py
Or run in background: nohup python3 watch-and-sync.py &
"""

import os
import subprocess
import time
from datetime import datetime

SYNC_DIR = os.path.expanduser("~/mega-sync")
CHECK_INTERVAL = 30  # seconds between checks

os.makedirs(SYNC_DIR, exist_ok=True)

def log(msg):
    t = datetime.now().strftime("%H:%M:%S")
    print(f"[{t}] {msg}")

class Watcher:
    def __init__(self):
        self.snapshot = {}

    def scan(self):
        """Get current file state: {name: (mtime, size)}"""
        state = {}
        if not os.path.isdir(SYNC_DIR):
            return state
        for f in os.listdir(SYNC_DIR):
            fp = os.path.join(SYNC_DIR, f)
            if f.startswith(".") or f == "gui":
                continue
            if os.path.isfile(fp):
                state[f] = (os.path.getmtime(fp), os.path.getsize(fp))
        return state

    def has_changes(self):
        current = self.scan()
        if current != self.snapshot:
            self.snapshot = current
            return True
        return False

    def git_push(self):
        try:
            # Stage all
            subprocess.run(["git", "add", "-A"], cwd=SYNC_DIR, capture_output=True, text=True)
            # Check if anything staged
            r = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=SYNC_DIR)
            if r.returncode == 0:
                return "no changes"
            # Commit
            ts = datetime.now().strftime("%Y-%m-%d %H:%M")
            subprocess.run(["git", "commit", "-m", f"📁 Auto-sync [{ts}]"], cwd=SYNC_DIR, capture_output=True, text=True)
            # Push
            r = subprocess.run(["git", "push"], cwd=SYNC_DIR, capture_output=True, text=True, timeout=60)
            return r.stdout.strip() or "pushed"
        except Exception as e:
            return f"error: {e}"

def main():
    log("📁 Mega Sync Auto-Watcher started")
    log(f"👀 Watching: {SYNC_DIR}")
    log(f"⏱  Checking every {CHECK_INTERVAL}s")
    log("")

    w = Watcher()
    w.snapshot = w.scan()  # initial snapshot

    last_push_ok = True

    while True:
        time.sleep(CHECK_INTERVAL)
        if not w.has_changes():
            if not last_push_ok:
                # try again if last push failed
                result = w.git_push()
                if "error" not in result:
                    last_push_ok = True
                    log(f"✅ Re-push successful")
            continue

        log("📦 Changes detected!")
        result = w.git_push()
        if "error" in result:
            log(f"❌ Push failed: {result}")
            last_push_ok = False
        else:
            log(f"✅ Synced: {result}")
            last_push_ok = True

        # quick status summary
        files = w.scan()
        log(f"📊 {len(files)} file(s) in sync folder")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Stopped.")
