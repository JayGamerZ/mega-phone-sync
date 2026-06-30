#!/bin/bash
# Mega Cloud Tool — now powered by GitHub Actions!
# Your phone just uses git — GitHub Actions does the actual Mega sync.

MEGA_DIR="$HOME/mega-sync"
REMOTE="${GIT_REMOTE:-origin}"
BRANCH="${GIT_BRANCH:-main}"

mkdir -p "$MEGA_DIR"

case "${1:-help}" in
  setup)
    echo "📦 Setting up Mega GitHub Sync..."
    cd "$MEGA_DIR"
    if [ -d ".git" ]; then
      echo "Already a git repo."
    else
      echo "Enter your GitHub username:"
      read GH_USER
      echo "Enter your repo name (e.g., mega-phone-sync):"
      read REPO_NAME
      git init
      git checkout -b "$BRANCH"
      git remote add "$REMOTE" "https://github.com/$GH_USER/$REPO_NAME.git"
      git add .
      git commit -m "Initial sync" 2>/dev/null
      git push -u "$REMOTE" "$BRANCH" 2>&1 || echo "Push failed. Did you create the repo on GitHub first?"
      echo "✅ Done! Now add MEGA_EMAIL and MEGA_PASSWORD as GitHub Secrets."
    fi
    ;;

  push)
    echo "📤 Sending files to Mega via GitHub..."
    cd "$MEGA_DIR"
    git add -A
    if git diff --cached --quiet; then
      echo "Nothing to push."
    else
      git commit -m "📱 Update $(date +'%Y-%m-%d %H:%M')"
      git push "$REMOTE" "$BRANCH"
      echo "✅ Pushed! GitHub Actions will sync to Mega momentarily."
    fi
    ;;

  pull)
    echo "📥 Getting files from Mega..."
    cd "$MEGA_DIR"
    git pull "$REMOTE" "$BRANCH"
    ;;

  status)
    echo "📁 Status:"
    cd "$MEGA_DIR" 2>/dev/null
    git status --short 2>/dev/null || echo "No changes"
    echo ""
    echo "Recent Mega activity:"
    git log --oneline -5 2>/dev/null || echo "No history yet"
    ;;

  daemon)
    # Lightweight background git sync (replaces old rclone daemon)
    echo "🔋 Starting battery-friendly git watcher..."
    echo "Running git pull every 30 min to check for Mega changes"
    while true; do
      cd "$MEGA_DIR"
      git pull "$REMOTE" "$BRANCH" -q 2>&1 | grep -v "Already up to date"
      sleep 1800  # 30 min — zero battery impact
    done
    ;;

  help|*)
    echo "📁 Mega Cloud Tool (GitHub Actions edition)"
    echo ""
    echo "Usage:  bash mega-tool.sh <command>"
    echo ""
    echo "  setup  - First-time GitHub repo config"
    echo "  push   - Upload files to Mega (via git)"
    echo "  pull   - Download Mega files (via git)"
    echo "  status - Check pending changes"
    echo "  daemon - Background git poller (optional)"
    echo ""
    echo "⚠️  Battery tips:"
    echo "   - Use 'push'/'pull' manually = zero battery"
    echo "   - Use 'daemon' = 1 git pull every 30min"
    echo "   - Old rclone daemon is retired! 🎉"
    ;;
esac
