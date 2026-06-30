#!/bin/bash
# Mega Sync GUI Launcher
# Start the web dashboard (open browser-friendly URL with your phone)
echo ""
echo "  📁 Mega Sync — GUI Launcher"
echo "  ──────────────────────────"
echo ""
echo "  Which mode?"
echo ""
echo "  1) 🌐 Web Dashboard  — open http://localhost:8080 in browser"
echo "  2) 👀 Auto-Watcher   — watches folder, syncs automatically"
echo "  3) 📤 Sync Now       — one-time push to Mega"
echo "  4) 📥 Pull Now       — one-time pull from Mega"
echo "  5) 📊 Status         — check sync status"
echo ""
read -p "  Choose [1-5]: " mode

case "$mode" in
  1)
    echo ""
    echo "  Starting web dashboard..."
    echo "  Open http://localhost:8080 in your phone browser"
    echo "  Press Ctrl+C to stop"
    echo ""
    python3 "$(dirname "$0")/dashboard.py"
    ;;
  2)
    echo ""
    echo "  Starting auto-watcher..."
    echo "  Just drop files in ~/mega-sync/ and they'll sync automatically"
    echo "  Press Ctrl+C to stop"
    echo ""
    python3 "$(dirname "$0")/watch-and-sync.py"
    ;;
  3)
    cd ~/mega-sync && bash mega-tool.sh push
    ;;
  4)
    cd ~/mega-sync && bash mega-tool.sh pull
    ;;
  5)
    cd ~/mega-sync && bash mega-tool.sh status
    ;;
  *)
    echo "Invalid choice"
    ;;
esac
