#!/bin/bash
# Phone-side helper — lightweight git wrapper for Mega GitHub Sync
# Usage: ./phone-helper.sh [push|pull|status|setup]

REPO_DIR="$HOME/mega-sync"
REMOTE="${GIT_REMOTE:-origin}"
BRANCH="${GIT_BRANCH:-main}"

setup_repo() {
  echo "📦 Setting up mega-sync repo..."
  mkdir -p "$REPO_DIR"
  cd "$REPO_DIR"

  if [ -d ".git" ]; then
    echo "Already a git repo. Skipping."
    return
  fi

  echo "Enter your GitHub username:"
  read GH_USER
  echo "Enter your repo name (e.g. mega-phone-sync):"
  read REPO_NAME

  git init
  git checkout -b "$BRANCH"
  git remote add "$REMOTE" "https://github.com/$GH_USER/$REPO_NAME.git"
  echo "✅ Repo configured! Now run: $0 push"
}

push_files() {
  echo "📤 Uploading files to GitHub (Mega sync will follow)..."
  cd "$REPO_DIR"
  git add -A
  if git diff --cached --quiet; then
    echo "Nothing to push."
    return
  fi
  echo "Enter a commit message (or press enter for auto):"
  read msg
  msg="${msg:-📱 Update $(date +'%Y-%m-%d %H:%M')}"
  git commit -m "$msg"
  git push "$REMOTE" "$BRANCH"
  echo "✅ Pushed! GitHub Actions will sync to Mega in ~1-2 min."
}

pull_files() {
  echo "📥 Pulling latest from GitHub (Mega changes)..."
  cd "$REPO_DIR"
  git pull "$REMOTE" "$BRANCH"
  echo "✅ Done! Files are in $REPO_DIR"
}

show_status() {
  cd "$REPO_DIR"
  echo "📁 Status:"
  git status --short 2>/dev/null || echo "No changes."
  echo ""
  echo "Latest commits:"
  git log --oneline -5 2>/dev/null || echo "No commits yet."
}

case "${1:-help}" in
  push)   push_files ;;
  pull)   pull_files ;;
  status) show_status ;;
  setup)  setup_repo ;;
  *)
    echo "📁 Mega GitHub Phone Helper"
    echo "Usage:"
    echo "  push   - Upload files → GitHub → Mega"
    echo "  pull   - Download Mega files → phone"
    echo "  status - Check pending changes"
    echo "  setup  - Configure git repo first time"
    ;;
esac
