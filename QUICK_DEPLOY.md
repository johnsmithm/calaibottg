# 🚀 Quick Deploy Guide

## Option 1: Railway (RECOMMENDED - 5 minutes)

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/calaitgbot.git
git push -u origin main

# 2. Go to railway.app
# 3. Login with GitHub
# 4. New Project → Deploy from GitHub
# 5. Select your repo
# 6. Add environment variables:
#    TELEGRAM_BOT_TOKEN=8751627408:AAFPUPCF1BsdodPuhM0h-pK3uJreJTrm3BE
#    GOOGLE_AI_API_KEY=AIzaSyCx7tT9mJfO_GHhFyEbqpDq442UKwAwRPc
# 7. Done! ✅
```

**Cost:** FREE ($5 credit/month - enough for this bot)
**Uptime:** 24/7
**Difficulty:** ⭐ Very Easy

---

## Option 2: Oracle Cloud (100% FREE FOREVER)

```bash
# 1. Create Oracle Cloud account (oracle.com/cloud/free)
# 2. Create VM (Always Free tier - Ubuntu)
# 3. SSH into VM
# 4. Run setup:

sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git -y

git clone https://github.com/YOUR_USERNAME/calaitgbot.git
cd calaitgbot

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Create .env file with your keys
nano .env

# 6. Create systemd service:
sudo nano /etc/systemd/system/calbot.service

# Add service configuration (see DEPLOYMENT.md)

# 7. Start service:
sudo systemctl enable calbot
sudo systemctl start calbot

# 8. Done! ✅
```

**Cost:** FREE FOREVER
**Uptime:** 24/7
**Difficulty:** ⭐⭐⭐ Medium

---

## Option 3: Render (Quick Test)

```bash
# 1. Go to render.com
# 2. New → Background Worker
# 3. Connect GitHub repo
# 4. Configure:
#    Build: pip install -r requirements.txt
#    Start: python bot.py
# 5. Add environment variables
# 6. Done! ✅
```

**Cost:** FREE
**Uptime:** Spins down after 15min inactivity ⚠️
**Difficulty:** ⭐⭐ Easy

---

## Need BotFather Commands?

Copy this to @BotFather → Edit Commands:

```
start - Start or restart onboarding
today - Show today's statistics
week - Show this week's statistics
month - Show this month's statistics
year - Show this year's statistics
progress - Show daily progress bar
profile - View your profile info
history - View recent meals (last 7 days)
reminders - View and manage meal reminders
delete - Delete last logged meal
reset - Reset all data and start over
stats - Show statistics (supports day/week/month/year)
help - Show help and commands
```

---

## Files Needed for Deployment

✅ Already created:
- `Procfile` - For Railway/Render
- `runtime.txt` - Specifies Python version
- `requirements.txt` - Dependencies
- `.env.example` - Template for environment variables
- `.gitignore` - Don't commit secrets

**DO NOT commit `.env` file to GitHub!**

---

## Troubleshooting

**Bot not responding?**
1. Check environment variables are set correctly
2. Check logs in platform dashboard
3. Verify bot token is correct

**Database not persisting?**
- Railway: ✅ Works fine
- Render: ⚠️ Use volumes or PostgreSQL
- Oracle: ✅ Works fine

---

## You're All Set! 🎉

Your bot is deployed and running 24/7!

Test it: Open Telegram → Search `@calaitg_bot` → Send `/start`
