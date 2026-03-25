# Deploy to PythonAnywhere

## Steps:

1. **Create account:** Go to [pythonanywhere.com](https://www.pythonanywhere.com) - Free tier available

2. **Upload your code:**
   - Open a Bash console
   - Clone your repo:
     ```bash
     git clone https://github.com/yourusername/calaitgbot.git
     cd calaitgbot
     ```

3. **Install dependencies:**
   ```bash
   pip3 install --user -r requirements.txt
   ```

4. **Create .env file:**
   ```bash
   nano .env
   ```
   Add your keys and save

5. **Create a scheduled task:**
   - Go to "Tasks" tab
   - Add: `python3 /home/yourusername/calaitgbot/bot.py`
   - Or use "Always-on task" (paid feature)

6. **Keep bot running:**
   Use screen or tmux:
   ```bash
   screen -S bot
   cd calaitgbot
   python3 bot.py
   # Press Ctrl+A then D to detach
   ```

**Pros:**
- Truly free
- Can run 24/7 with workarounds
- Persistent storage

**Cons:**
- More manual setup
- Free tier has CPU limitations
- Need to keep session alive
