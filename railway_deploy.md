# Deploy to Railway.app

## Steps:

1. **Create account:** Go to [railway.app](https://railway.app) and sign up with GitHub

2. **Install Railway CLI (optional):**
```bash
npm i -g @railway/cli
```

3. **Deploy via GitHub:**
   - Push your code to GitHub
   - Go to Railway dashboard
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect Python

4. **Set Environment Variables:**
   In Railway dashboard:
   - Click on your project
   - Go to "Variables" tab
   - Add:
     - `TELEGRAM_BOT_TOKEN` = `8751627408:AAFPUPCF1BsdodPuhM0h-pK3uJreJTrm3BE`
     - `GOOGLE_AI_API_KEY` = `AIzaSyCx7tT9mJfO_GHhFyEbqpDq442UKwAwRPc`

5. **Add Procfile:**
   Railway needs this to know how to run your bot

6. **Deploy!**
   - Railway will automatically deploy
   - Bot runs 24/7

**Pros:**
- Easy setup
- Auto-deploys from GitHub
- Persistent storage (SQLite works)
- Good free tier

**Cons:**
- Free tier limited to $5/month credit
