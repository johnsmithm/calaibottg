# 🚀 Free Deployment Guide

## Quick Comparison

| Platform | Free Tier | 24/7 Uptime | Ease | Best For |
|----------|-----------|-------------|------|----------|
| **Railway** | $5/month credit | ✅ Yes | ⭐⭐⭐⭐⭐ | Easiest option |
| **Oracle Cloud** | Forever free | ✅ Yes | ⭐⭐⭐ | Best long-term |
| **Render** | 750 hrs/month | ❌ No (spins down) | ⭐⭐⭐⭐ | Good for testing |
| **PythonAnywhere** | Limited CPU | ⚠️ With workarounds | ⭐⭐⭐ | Simple setup |
| **Fly.io** | 3 shared VMs | ✅ Yes | ⭐⭐⭐⭐ | Modern platform |

---

## 🏆 Recommended: Railway.app (Easiest)

### Why Railway?
- ✅ Simplest deployment process
- ✅ Auto-deploys from GitHub
- ✅ True 24/7 uptime
- ✅ $5 free credit/month (enough for this bot)
- ✅ SQLite persistence works out of the box

### Quick Start:

1. **Push to GitHub:**
   ```bash
   cd /Users/ion/apps/calaitgbot
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/calaitgbot.git
   git push -u origin main
   ```

2. **Deploy on Railway:**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python

3. **Add Environment Variables:**
   - Click on your project
   - Go to "Variables" tab
   - Add:
     ```
     TELEGRAM_BOT_TOKEN=8751627408:AAFPUPCF1BsdodPuhM0h-pK3uJreJTrm3BE
     GOOGLE_AI_API_KEY=AIzaSyCx7tT9mJfO_GHhFyEbqpDq442UKwAwRPc
     ```

4. **Deploy!**
   - Railway automatically deploys
   - Watch logs in the dashboard
   - Bot is live! 🎉

---

## 🔥 Best for Long-term: Oracle Cloud

### Why Oracle Cloud?
- ✅ **100% free forever** (no trial period)
- ✅ Always-Free tier never expires
- ✅ True 24/7 uptime
- ✅ Full VM control
- ✅ 2 free VMs + storage

### Setup Steps:

See `oracle_cloud_deploy.md` for detailed instructions.

**TL;DR:**
1. Create Oracle Cloud account
2. Launch Always Free VM (Ubuntu)
3. SSH into VM
4. Clone repo, install dependencies
5. Create systemd service for auto-restart
6. Done!

---

## 📝 Before Deploying

### 1. Create `.gitignore` (if using GitHub):
```
__pycache__/
*.pyc
.env
*.db
*.log
venv/
photos/
voice/
test_gemini.py
```

### 2. Update `.env` handling:

The bot already uses `python-dotenv` to load environment variables from `.env` file.

For deployment platforms, set environment variables in their dashboard instead.

### 3. Database Persistence:

**SQLite** (current setup):
- ✅ Works on: Railway, Oracle Cloud, PythonAnywhere
- ❌ Issues on: Render (ephemeral storage), Fly.io (ephemeral)

**For platforms with ephemeral storage:**
Consider switching to PostgreSQL (free on most platforms).

---

## 🎯 Step-by-Step: Railway Deployment

### 1. Prepare Repository

```bash
cd /Users/ion/apps/calaitgbot

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Calorie tracker bot ready for deployment"

# Create GitHub repo and push
# (Create repo on GitHub first)
git remote add origin https://github.com/YOUR_USERNAME/calaitgbot.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Click "Login" → "Login with GitHub"
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `calaitgbot` repository
6. Railway will detect Python and install dependencies

### 3. Configure Environment Variables

1. Click on your deployed service
2. Go to "Variables" tab
3. Click "Add Variable"
4. Add each variable:
   - **Variable:** `TELEGRAM_BOT_TOKEN`
     **Value:** `8751627408:AAFPUPCF1BsdodPuhM0h-pK3uJreJTrm3BE`

   - **Variable:** `GOOGLE_AI_API_KEY`
     **Value:** `AIzaSyCx7tT9mJfO_GHhFyEbqpDq442UKwAwRPc`

### 4. Check Deployment

1. Go to "Deployments" tab
2. Click on latest deployment
3. View logs - you should see:
   ```
   Bot started!
   Application started
   ```

### 5. Test Your Bot

1. Open Telegram
2. Search for your bot: `@calaitg_bot`
3. Send `/start`
4. Bot should respond! 🎉

---

## 🔧 Troubleshooting

### Bot not responding?

**Check logs:**
- Railway: Click deployment → View logs
- Oracle Cloud: `sudo journalctl -u calbot -f`

**Common issues:**
1. **Wrong API keys** - Double-check environment variables
2. **Gemini model error** - Ensure `gemini-2.5-flash` is available
3. **Port binding** - Telegram bots don't need ports, using polling

### Database issues?

**SQLite file not persisting:**
- Railway: Should work by default
- Render/Fly.io: Use volume mounts or switch to PostgreSQL

---

## 💡 Tips

1. **Monitor usage:**
   - Railway: Check usage in dashboard
   - Oracle: Monitor in cloud console

2. **Auto-updates:**
   - Railway: Auto-deploys on git push
   - Oracle: Set up git pull cron job

3. **Logs:**
   - Always check logs first when debugging
   - Most platforms have real-time log viewing

4. **Backups:**
   - Download `calorie_tracker.db` regularly
   - Railway: Can access via SSH (paid feature)
   - Oracle: Use `scp` to download

---

## 🎓 Need Help?

- Railway docs: [docs.railway.app](https://docs.railway.app)
- Oracle Cloud: [oracle.com/cloud/free](https://oracle.com/cloud/free)
- Telegram Bot API: [core.telegram.org/bots/api](https://core.telegram.org/bots/api)

---

## ✅ You're Done!

Your bot is now running 24/7 in the cloud! 🚀

Users can:
- Send food photos
- Get AI nutritional analysis
- Track calories and macros
- View statistics
- Set meal reminders

All for **FREE**! 🎉
