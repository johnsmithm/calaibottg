#!/bin/bash

# Stop Calorie Tracker Bot

cd "$(dirname "$0")"

echo "🛑 Stopping Calorie Tracker Bot..."

if [ ! -f "bot.pid" ]; then
    echo "❌ No bot.pid file found. Bot may not be running."

    # Try to find and kill any running bot processes
    PIDS=$(ps aux | grep "[p]ython bot.py" | awk '{print $2}')
    if [ ! -z "$PIDS" ]; then
        echo "Found running bot process(es): $PIDS"
        kill $PIDS 2>/dev/null
        echo "✅ Bot stopped"
    else
        echo "No running bot processes found"
    fi
    exit 0
fi

PID=$(cat bot.pid)

if ps -p $PID > /dev/null 2>&1; then
    kill $PID
    echo "✅ Bot stopped (PID: $PID)"
    rm bot.pid
else
    echo "⚠️  Process $PID not found (may have already stopped)"
    rm bot.pid
fi
