# Deploy to Render.com

## Steps:

1. **Create account:** Go to [render.com](https://render.com) and sign up

2. **Deploy:**
   - Click "New +" → "Background Worker"
   - Connect your GitHub repository
   - Configure:
     - **Name:** calorie-tracker-bot
     - **Runtime:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `python bot.py`

3. **Set Environment Variables:**
   - `TELEGRAM_BOT_TOKEN` = `8751627408:AAFPUPCF1BsdodPuhM0h-pK3uJreJTrm3BE`
   - `GOOGLE_AI_API_KEY` = `AIzaSyCx7tT9mJfO_GHhFyEbqpDq442UKwAwRPc`

4. **Deploy!**

**Pros:**
- Truly free tier (with limitations)
- Easy GitHub integration
- Auto-redeploy on push

**Cons:**
- Free tier spins down after 15 min inactivity
- Not ideal for bots that need 24/7 uptime
- Limited to 750 hours/month
