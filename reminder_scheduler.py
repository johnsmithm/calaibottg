import schedule
import time
import threading
from datetime import datetime
import asyncio
import pytz
import os
import logging
from database import Database
from translations import t, get_user_lang

logger = logging.getLogger(__name__)


class ReminderScheduler:
    def __init__(self, bot, db: Database, event_loop=None):
        self.bot = bot
        self.db = db
        self.running = False
        self.event_loop = event_loop  # Store the event loop reference

    def send_reminder(self, user_id, meal_type):
        """Send meal reminder to user"""
        # Use stored event loop or try to get the running one
        try:
            loop = self.event_loop
            if loop is None:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = asyncio.get_event_loop()

            asyncio.run_coroutine_threadsafe(
                self._send_reminder_async(user_id, meal_type),
                loop
            )
            logger.info(f"Scheduled reminder for user {user_id}, meal: {meal_type}")
        except Exception as e:
            logger.error(f"Error scheduling reminder for user {user_id}: {e}", exc_info=True)

    async def _send_reminder_async(self, user_id, meal_type):
        """Async wrapper for sending reminders"""
        try:
            # Get user's language
            user = self.db.get_user(user_id)
            lang = get_user_lang(user)

            # Get translated message
            message_key = f'reminder_{meal_type}'
            message = t(message_key, lang)

            await self.bot.send_message(
                chat_id=user_id,
                text=message
            )
            logger.info(f"Sent {meal_type} reminder to user {user_id} in {lang}")
        except Exception as e:
            logger.error(f"Error sending reminder to {user_id}: {e}", exc_info=True)

    def check_reminders(self):
        """Check and send reminders for all users"""
        try:
            # Use Moldova timezone
            tz = pytz.timezone(os.getenv('TIMEZONE', 'Europe/Chisinau'))
            current_time = datetime.now(tz).strftime('%H:%M')

            # Get all users from database
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users')
            users = cursor.fetchall()

            reminders_sent = 0
            for user_row in users:
                user_id = user_row['user_id']
                meal_times = self.db.get_meal_times(user_id)

                for meal_type, meal_time in meal_times.items():
                    if meal_time == current_time:
                        self.send_reminder(user_id, meal_type)
                        reminders_sent += 1

            if reminders_sent > 0:
                logger.info(f"Checked reminders at {current_time}, sent {reminders_sent} reminders")

            conn.close()
        except Exception as e:
            logger.error(f"Error checking reminders: {e}", exc_info=True)

    def run_scheduler(self):
        """Run the scheduler in a loop"""
        logger.info("Reminder scheduler thread started")
        # Check every minute
        schedule.every(1).minutes.do(self.check_reminders)

        while self.running:
            schedule.run_pending()
            time.sleep(30)  # Sleep for 30 seconds between checks

        logger.info("Reminder scheduler thread stopped")

    def start(self):
        """Start the scheduler in a background thread"""
        self.running = True
        scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("Reminder scheduler started in background thread")

    def stop(self):
        """Stop the scheduler"""
        self.running = False
