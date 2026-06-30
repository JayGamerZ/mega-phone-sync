# 📁 Mega Cloud Sync via GitHub Actions

Zero battery drain on your phone. GitHub Actions does all the work.

## How it works

```
┌──────────────┐    git push     ┌─────────────┐   rclone   ┌────────┐
│  Your Phone  │ ──────────────▶ │ GitHub Repo │ ──────────▶ │  Mega  │
│  (no rclone) │ ◀────────────── │  + Actions  │ ◀────────── │  .nz   │
└──────────────┘    git pull     └─────────────┘   rclone   └────────┘
```

## Setup (10 minutes)

### 1. Create a GitHub repo & push your files
```bash
# On your phone (in termux / this environment)
cd ~/mega-sync

# Initialize git
git init
git add .
git commit -m "Initial upload"

# Create repo on GitHub (install gh or do it manually)
gh repo create mega-phone-sync --public --push --source=.
# OR: create on github.com first, then:
# git remote add origin https://github.com/YOUR_USER/mega-phone-sync.git
# git push -u origin main
```

### 2. Add secrets to GitHub
Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret | Value |
|--------|-------|
| `MEGA_EMAIL` | jayantsharma1469@gmail.com |
| `MEGA_PASSWORD` | Jayant@102 |

### 3. Enable Actions
Go to your repo → **Actions** tab → **Enable** the workflow

## Daily usage

```bash
# 📤 Upload files to Mega (1 second, no battery drain):
cd ~/mega-sync
cp ~/new-photo.jpg .
git add .
git commit -m "Added photo"
git push
# ✅ GitHub Actions handles the Mega upload!

# 📥 Get files from Mega (just syncs the repo):
git pull
# ✅ New files from Mega appear in ~/mega-sync/
```

## What happens under the hood

| Trigger | What GitHub Actions does |
|---------|--------------------------|
| You **git push** | Instantly copies files to Mega |
| Every **30 min** | Checks Mega for new/changed files |
| **Manual trigger** | GitHub UI → Actions → "Run workflow" |

## Smart detection
If nothing changed on Mega, the 30-minute check does nothing and uses 0 action minutes. It only runs the sync when files are actually different.

## Pro tips
- The repo acts as your file **version history** too
- Make it **private** if you want (just stay within 2000 min/month limit)
- Change the schedule in `.github/workflows/sync.yml` if you want faster/slower checks
