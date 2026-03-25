# Deploy to Fly.io

## Steps:

1. **Install flyctl:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Sign up:**
   ```bash
   flyctl auth signup
   ```

3. **Launch app:**
   ```bash
   cd /Users/ion/apps/calaitgbot
   flyctl launch
   ```
   - Answer prompts
   - Don't deploy yet

4. **Set secrets:**
   ```bash
   flyctl secrets set TELEGRAM_BOT_TOKEN="8751627408:AAFPUPCF1BsdodPuhM0h-pK3uJreJTrm3BE"
   flyctl secrets set GOOGLE_AI_API_KEY="AIzaSyCx7tT9mJfO_GHhFyEbqpDq442UKwAwRPc"
   ```

5. **Deploy:**
   ```bash
   flyctl deploy
   ```

**Pros:**
- Modern platform
- Easy CLI
- Good free tier (3 shared VMs)
- Fast deploys

**Cons:**
- Credit card required (won't charge)
- Free tier limited
