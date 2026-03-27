import schedule
import time
import threading
from datetime import datetime
import asyncio
import pytz
import os
from database import Database


class ReminderScheduler:
    def __init__(self, bot, db: Database):
        self.bot = bot
        self.db = db
        self.running = False

    def send_reminder(self, user_id, meal_type):
        """Send meal reminder to user"""
        # Get the running event loop and schedule the coroutine
        try:
            loop = asyncio.get_event_loop()
            asyncio.run_coroutine_threadsafe(
                self._send_reminder_async(user_id, meal_type),
                loop
            )
        except Exception as e:
            print(f"Error scheduling reminder for user {user_id}: {e}")

    async def _send_reminder_async(self, user_id, meal_type):
        """Async wrapper for sending reminders"""
        messages = {
            'breakfast': '🌅 Good morning! Time for breakfast. Send me a photo of your meal!',
            'lunch': '🌞 Lunch time! Don\'t forget to log your meal.',
            'dinner': '🌙 Dinner time! Remember to track your evening meal.'
        }

        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=messages.get(meal_type, 'Time to log your meal!')
            )
        except Exception as e:
            print(f"Error sending reminder to {user_id}: {e}")

    def check_reminders(self):
        """Check and send reminders for all users"""
        # Use Moldova timezone
        tz = pytz.timezone(os.getenv('TIMEZONE', 'Europe/Chisinau'))
        current_time = datetime.now(tz).strftime('%H:%M')

        # Get all users from database
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users')
        users = cursor.fetchall()

        for user_row in users:
            user_id = user_row['user_id']
            meal_times = self.db.get_meal_times(user_id)

            for meal_type, meal_time in meal_times.items():
                if meal_time == current_time:
                    self.send_reminder(user_id, meal_type)

        conn.close()

    def run_scheduler(self):
        """Run the scheduler in a loop"""
        # Check every minute
        schedule.every(1).minutes.do(self.check_reminders)

        while self.running:
            schedule.run_pending()
            time.sleep(30)  # Sleep for 30 seconds between checks

    def start(self):
        """Start the scheduler in a background thread"""
        self.running = True
        scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()

    def stop(self):
        """Stop the scheduler"""
        self.running = False
