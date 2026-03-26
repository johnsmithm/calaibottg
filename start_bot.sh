#!/bin/bash

# Start Calorie Tracker Bot
# This script activates the virtual environment and starts the bot

cd "$(dirname "$0")"

echo "🤖 Starting Calorie Tracker Bot..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with required environment variables"
    exit 1
fi

# Check if another instance is running
if [ -f "bot.pid" ]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  Bot is already running (PID: $PID)"
        echo "Use ./stop_bot.sh to stop it first"
        exit 1
    fi
fi

# Activate virtual environment and start bot
source venv/bin/activate

# Start bot in background
nohup python bot.py > bot.log 2>&1 &
BOT_PID=$!

# Save PID
echo $BOT_PID > bot.pid

echo "✅ Bot started successfully!"
echo "📝 PID: $BOT_PID"
echo "📋 Logs: tail -f bot.log"
echo ""
echo "Bot username: @calaitgdev_bot"
echo "Bot token: 8617284502:AAFBmVfVKeW10XXXDBlPmKvaYjhiedoLUJY (dev)"
echo ""
echo "Commands:"
echo "  ./stop_bot.sh  - Stop the bot"
echo "  tail -f bot.log - View live logs"
