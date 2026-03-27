import os
import logging
import re
import html
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv
import speech_recognition as sr
from pydub import AudioSegment
import tempfile

from database import Database
from ai_analyzer import AIAnalyzer
from calorie_calculator import calculate_daily_calorie_target
from reminder_scheduler import ReminderScheduler
from translations import t, get_user_lang, SPEECH_LANG_CODES

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Admin user ID
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0'))

# Initialize components
db = Database()
ai = AIAnalyzer()

# Conversation states
NAME, HEIGHT, WEIGHT, GOAL, GOAL_SPEED, BREAKFAST_TIME, LUNCH_TIME, DINNER_TIME, API_KEY, EDIT_CALORIES = range(10)

# User data storage for onboarding
user_onboarding_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - begins user onboarding"""
    user_id = update.effective_user.id
    username = update.effective_user.username or 'unknown'

    # Log user info for admin setup
    logger.info(f"User attempting /start - ID: {user_id}, Username: @{username}")

    # Check if user exists
    user = db.get_user(user_id)

    if user:
        lang = get_user_lang(user)
        await update.message.reply_text(
            t('welcome_back', lang, name=user['name'])
        )
        return ConversationHandler.END

    # Start onboarding
    await update.message.reply_text(
        t('onboarding_welcome', 'en')
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user's name"""
    user_id = update.effective_user.id
    name = update.message.text.strip()

    user_onboarding_data[user_id] = {'name': name}

    await update.message.reply_text(
        f"Nice to meet you, {name}! 😊\n\n"
        "What's your height in cm?"
    )
    return HEIGHT


async def get_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user's height"""
    user_id = update.effective_user.id

    try:
        height = float(update.message.text.strip())
        user_onboarding_data[user_id]['height'] = height

        await update.message.reply_text(
            "Great! What's your current weight in kg?"
        )
        return WEIGHT
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid number for height (e.g., 175)"
        )
        return HEIGHT


async def get_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user's weight"""
    user_id = update.effective_user.id

    try:
        weight = float(update.message.text.strip())
        user_onboarding_data[user_id]['weight'] = weight

        keyboard = [
            [InlineKeyboardButton("Lose Weight", callback_data="goal_lose_weight")],
            [InlineKeyboardButton("Gain Weight", callback_data="goal_gain_weight")],
            [InlineKeyboardButton("Maintain Weight", callback_data="goal_maintain")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "What's your goal?",
            reply_markup=reply_markup
        )
        return GOAL
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid number for weight (e.g., 70)"
        )
        return WEIGHT


async def get_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user's goal"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    goal = query.data.replace('goal_', '')
    user_onboarding_data[user_id]['goal'] = goal

    if goal == 'maintain':
        # Skip goal speed for maintain
        await query.edit_message_text(
            "Great! What time do you usually eat breakfast? (e.g., 08:00 or 8am)"
        )
        return BREAKFAST_TIME

    keyboard = [
        [InlineKeyboardButton("Slow (0.25 kg/week)", callback_data="speed_slow")],
        [InlineKeyboardButton("Moderate (0.5 kg/week)", callback_data="speed_moderate")],
        [InlineKeyboardButton("Fast (0.75 kg/week)", callback_data="speed_fast")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "How fast do you want to reach your goal?",
        reply_markup=reply_markup
    )
    return GOAL_SPEED


async def get_goal_speed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user's goal speed"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    goal_speed = query.data.replace('speed_', '')
    user_onboarding_data[user_id]['goal_speed'] = goal_speed

    await query.edit_message_text(
        "Perfect! What time do you usually eat breakfast? (e.g., 08:00 or 8am)"
    )
    return BREAKFAST_TIME


def parse_time(time_str):
    """Parse time string to HH:MM format"""
    time_str = time_str.strip().lower().replace(' ', '')

    # Handle formats like 8am, 8:30pm, 08:00, 20:30
    if 'am' in time_str or 'pm' in time_str:
        is_pm = 'pm' in time_str
        time_str = time_str.replace('am', '').replace('pm', '')

        if ':' in time_str:
            hour, minute = time_str.split(':')
        else:
            hour = time_str
            minute = '00'

        hour = int(hour)
        if is_pm and hour != 12:
            hour += 12
        elif not is_pm and hour == 12:
            hour = 0

        return f"{hour:02d}:{minute}"
    else:
        if ':' in time_str:
            parts = time_str.split(':')
            return f"{int(parts[0]):02d}:{parts[1]}"
        else:
            return f"{int(time_str):02d}:00"


async def get_breakfast_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get breakfast time"""
    user_id = update.effective_user.id

    try:
        time_str = update.message.text.strip()
        breakfast_time = parse_time(time_str)
        user_onboarding_data[user_id]['breakfast_time'] = breakfast_time

        await update.message.reply_text(
            "Got it! What time do you usually eat lunch? (e.g., 13:00 or 1pm)"
        )
        return LUNCH_TIME
    except:
        await update.message.reply_text(
            "Please enter a valid time (e.g., 08:00 or 8am)"
        )
        return BREAKFAST_TIME


async def get_lunch_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get lunch time"""
    user_id = update.effective_user.id

    try:
        time_str = update.message.text.strip()
        lunch_time = parse_time(time_str)
        user_onboarding_data[user_id]['lunch_time'] = lunch_time

        await update.message.reply_text(
            "Almost done! What time do you usually eat dinner? (e.g., 19:00 or 7pm)"
        )
        return DINNER_TIME
    except:
        await update.message.reply_text(
            "Please enter a valid time (e.g., 13:00 or 1pm)"
        )
        return LUNCH_TIME


async def get_dinner_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get dinner time and ask for API key"""
    user_id = update.effective_user.id

    try:
        time_str = update.message.text.strip()
        dinner_time = parse_time(time_str)
        user_onboarding_data[user_id]['dinner_time'] = dinner_time

        # Ask for API key
        await update.message.reply_text(
            "🔑 *API Key Setup*\n\n"
            "To use this bot, you need either:\n"
            "1️⃣ Admin approval (contact @imosnoi)\n"
            "2️⃣ Your own Gemini API key\n\n"
            "If you have a Gemini API key, send it now.\n"
            "Otherwise, send /skip and wait for admin approval.\n\n"
            "💡 Get a free API key at:\n"
            "https://aistudio.google.com/app/apikey",
            parse_mode='Markdown'
        )
        return API_KEY
    except:
        await update.message.reply_text(
            "Please enter a valid time (e.g., 19:00 or 7pm)"
        )
        return DINNER_TIME


async def skip_api_key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Skip API key during onboarding (wait for admin approval)."""
    user_id = update.effective_user.id
    username = update.effective_user.username or 'unknown'

    if user_id not in user_onboarding_data:
        await update.message.reply_text("No active onboarding found. Use /start to begin.")
        return ConversationHandler.END

    data = user_onboarding_data[user_id]
    goal_speed = data.get('goal_speed', 'moderate')

    daily_calories = calculate_daily_calorie_target(
        weight=data['weight'],
        height=data['height'],
        goal=data['goal'],
        goal_speed=goal_speed
    )

    # Save user without API key (pending approval)
    db.create_user(
        user_id=user_id,
        username=username,
        name=data['name'],
        height=data['height'],
        weight=data['weight'],
        goal=data['goal'],
        goal_speed=goal_speed,
        daily_calorie_target=daily_calories,
        gemini_api_key=None
    )

    # Save meal times
    db.set_meal_time(user_id, 'breakfast', data['breakfast_time'])
    db.set_meal_time(user_id, 'lunch', data['lunch_time'])
    db.set_meal_time(user_id, 'dinner', data['dinner_time'])

    del user_onboarding_data[user_id]

    await update.message.reply_text(
        f"✅ All set, {data['name']}!\n\n"
        f"⏳ Waiting for admin approval. You'll be notified when approved.\n\n"
        f"📊 Your daily calorie target: {daily_calories} kcal\n\n"
        f"🔔 Reminders:\n"
        f"• Breakfast: {data['breakfast_time']}\n"
        f"• Lunch: {data['lunch_time']}\n"
        f"• Dinner: {data['dinner_time']}\n\n"
        f"🔒 You cannot upload photos or log meals until you are approved.\n\n"
        f"Use /help to see all commands."
    )

    return ConversationHandler.END


async def get_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get API key and complete onboarding"""
    user_id = update.effective_user.id
    username = update.effective_user.username or 'unknown'
    api_key_input = update.message.text.strip()

    # Store API key if provided (not 'skip')
    normalized = api_key_input.strip().lower()
    gemini_api_key = None if normalized in ('skip', '/skip') else api_key_input

    # Calculate daily calorie target
    data = user_onboarding_data[user_id]
    goal_speed = data.get('goal_speed', 'moderate')

    daily_calories = calculate_daily_calorie_target(
        weight=data['weight'],
        height=data['height'],
        goal=data['goal'],
        goal_speed=goal_speed
    )

    # Save user to database
    db.create_user(
        user_id=user_id,
        username=username,
        name=data['name'],
        height=data['height'],
        weight=data['weight'],
        goal=data['goal'],
        goal_speed=goal_speed,
        daily_calorie_target=daily_calories,
        gemini_api_key=gemini_api_key
    )

    # Save meal times
    db.set_meal_time(user_id, 'breakfast', data['breakfast_time'])
    db.set_meal_time(user_id, 'lunch', data['lunch_time'])
    db.set_meal_time(user_id, 'dinner', data['dinner_time'])

    # Clear onboarding data
    del user_onboarding_data[user_id]

    if gemini_api_key:
        status_msg = "✅ Your API key has been saved!"
        instructions = (
            "📸 Send me a photo of your meal to get started!\n"
            "🎤 You can also send voice messages or text descriptions.\n\n"
            "Use /help to see all commands."
        )
    else:
        status_msg = "⏳ Waiting for admin approval. You'll be notified when approved."
        instructions = (
            "🔒 You cannot upload photos or log meals until you are approved.\n\n"
            "Please wait for admin approval, or use /start to restart onboarding and provide your own Gemini API key.\n\n"
            "Use /help to see all commands."
        )

    await update.message.reply_text(
        f"✅ All set, {data['name']}!\n\n"
        f"{status_msg}\n\n"
        f"📊 Your daily calorie target: {daily_calories} kcal\n\n"
        f"🔔 Reminders:\n"
        f"• Breakfast: {data['breakfast_time']}\n"
        f"• Lunch: {data['lunch_time']}\n"
        f"• Dinner: {data['dinner_time']}\n\n"
        f"{instructions}"
    )

    return ConversationHandler.END


async def cancel_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel onboarding"""
    user_id = update.effective_user.id
    if user_id in user_onboarding_data:
        del user_onboarding_data[user_id]

    await update.message.reply_text(
        "Onboarding cancelled. Use /start to begin again."
    )
    return ConversationHandler.END


def format_meal_message(meal_data):
    """Format meal data with ingredient breakdown"""
    message = f"📊 *Nutritional Information:*\n\n"
    message += f"🍽 {meal_data['description']}\n"
    message += f"🍴 Meal Type: {meal_data['meal_type'].title()}\n\n"

    # Show ingredients if available
    if 'ingredients' in meal_data and meal_data['ingredients']:
        message += f"*INGREDIENTS:*\n"
        for ing in meal_data['ingredients']:
            message += f"• {ing['name']} ({ing['amount']}) - {ing['calories']} kcal\n"
        message += f"\n*TOTAL:*\n"

    message += f"⚡️ Calories: {meal_data['calories']} kcal\n"
    message += f"🥩 Protein: {meal_data['protein']}g\n"
    message += f"🍞 Carbs: {meal_data['carbs']}g\n"
    message += f"🥑 Fat: {meal_data['fat']}g\n"
    message += f"🌾 Fiber: {meal_data['fiber']}g\n"
    message += f"🍬 Sugar: {meal_data['sugar']}g\n\n"
    message += f"Save this meal?"

    return message


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads"""
    user_id = update.effective_user.id

    # Check if user exists
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text(
            "Please complete onboarding first with /start"
        )
        return

    # Check if user is approved or has own API key
    if not user.get('is_approved') and not user.get('gemini_api_key'):
        await update.message.reply_text(
            "⏳ Your account is pending approval.\n\n"
            "Please wait for admin approval, or restart onboarding with /start to provide your own Gemini API key."
        )
        return

    await update.message.reply_text("🔍 Analyzing your meal...")

    try:
        # Download photo
        photo_file = await update.message.photo[-1].get_file()

        # Create photos directory if it doesn't exist
        os.makedirs('photos', exist_ok=True)

        # Save photo
        photo_path = f"photos/{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        await photo_file.download_to_drive(photo_path)

        # Use user's API key if they have one
        if user.get('gemini_api_key'):
            user_ai = AIAnalyzer(api_key=user['gemini_api_key'])
            meal_data, usage = user_ai.analyze_food_image(photo_path)
        else:
            meal_data, usage = ai.analyze_food_image(photo_path)

        meal_data['image_path'] = photo_path

        # Save to pending meals
        db.save_pending_meal(user_id, meal_data)

        # Send results with save/edit/cancel buttons
        keyboard = [
            [InlineKeyboardButton("✅ Save", callback_data="save_meal")],
            [InlineKeyboardButton("✏️ Edit Calories", callback_data="edit_calories")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_meal")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Format message with token usage
        message = format_meal_message(meal_data)
        message += f"\n\n💡 *AI Usage*\n"
        message += f"📊 Tokens: {usage['total_tokens']:,} (in: {usage['prompt_tokens']:,}, out: {usage['output_tokens']:,})\n"
        message += f"💰 Cost: ${usage['cost_usd']:.6f}"

        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error analyzing photo: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't analyze this image. Please try again."
        )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages"""
    user_id = update.effective_user.id

    # Check if user exists
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text(
            "Please complete onboarding first with /start"
        )
        return

    # Check if user is approved or has own API key
    if not user.get('is_approved') and not user.get('gemini_api_key'):
        await update.message.reply_text(
            "⏳ Your account is pending approval.\n\n"
            "Please wait for admin approval, or restart onboarding with /start to provide your own Gemini API key."
        )
        return

    lang = get_user_lang(user)
    await update.message.reply_text(t('processing_voice', lang))

    try:
        # Download voice file
        voice_file = await update.message.voice.get_file()

        # Create voice directory if it doesn't exist
        os.makedirs('voice', exist_ok=True)

        # Save voice file
        voice_path = f"voice/{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ogg"
        await voice_file.download_to_drive(voice_path)

        # Convert to WAV for speech recognition
        audio = AudioSegment.from_ogg(voice_path)
        wav_path = voice_path.replace('.ogg', '.wav')
        audio.export(wav_path, format="wav")

        # Transcribe using user's language
        lang_code = SPEECH_LANG_CODES.get(get_user_lang(user), 'en-US')
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language=lang_code)

        # Clean up
        os.remove(voice_path)
        os.remove(wav_path)

        # Use AI to understand intent (same as text handler)
        intent = ai.parse_user_intent(text, user)

        # Handle different intents (similar to text handler)
        if intent['action'] == 'get_stats':
            # Redirect to text handler logic
            period = intent.get('period', 'day')
            now = datetime.now()

            if period == 'day':
                start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end = start + timedelta(days=1)
                period_name = "Today"
            elif period == 'week':
                start = now - timedelta(days=now.weekday())
                start = start.replace(hour=0, minute=0, second=0, microsecond=0)
                end = start + timedelta(days=7)
                period_name = "This Week"
            elif period == 'month':
                start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if now.month == 12:
                    end = start.replace(year=now.year+1, month=1)
                else:
                    end = start.replace(month=now.month+1)
                period_name = "This Month"
            else:
                start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end = start + timedelta(days=1)
                period_name = "Today"

            stats = db.get_stats(user_id, start, end)

            if not stats or stats['meal_count'] == 0:
                await update.message.reply_text(f"📝 I heard: \"{text}\"\n\nNo meals recorded for {period_name.lower()}.")
                return

            total_cals = stats['total_calories'] or 0
            message = (
                f"📝 I heard: \"{text}\"\n\n"
                f"📊 *{period_name} Statistics*\n\n"
                f"🍽 Meals: {stats['meal_count']}\n"
                f"⚡️ Total calories: {int(total_cals)} kcal\n"
                f"🥩 Protein: {int(stats['total_protein'] or 0)}g\n"
                f"🍞 Carbs: {int(stats['total_carbs'] or 0)}g\n"
                f"🥑 Fat: {int(stats['total_fat'] or 0)}g"
            )
            await update.message.reply_text(message, parse_mode='Markdown')
            return

        elif intent['action'] == 'get_profile':
            message = (
                f"📝 I heard: \"{text}\"\n\n"
                f"👤 *Your Profile*\n\n"
                f"📛 Name: {user['name']}\n"
                f"⚖️ Weight: {user['weight']} kg\n"
                f"📏 Height: {user['height']} cm\n"
                f"🎯 Goal: {user['goal'].replace('_', ' ').title()}\n"
                f"🍽 Daily Target: {int(user['daily_calorie_target'])} kcal"
            )
            await update.message.reply_text(message, parse_mode='Markdown')
            return

        # Otherwise, treat as meal logging
        meal_data, usage = ai.analyze_text_meal(text)

        # Ensure meal_type is set (fallback to 'snack' if not provided)
        if 'meal_type' not in meal_data or not meal_data['meal_type']:
            meal_data['meal_type'] = 'snack'

        # Save to pending meals
        db.save_pending_meal(user_id, meal_data)

        # Send results with save/edit/cancel buttons
        keyboard = [
            [InlineKeyboardButton("✅ Save", callback_data="save_meal")],
            [InlineKeyboardButton("✏️ Edit Calories", callback_data="edit_calories")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_meal")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = (
            f"📝 I heard: \"{text}\"\n\n"
            f"📊 *Nutritional Information:*\n\n"
            f"🍽 {meal_data['description']}\n"
            f"🍴 Meal Type: {meal_data['meal_type'].title()}\n\n"
            f"⚡️ Calories: {meal_data['calories']} kcal\n"
            f"🥩 Protein: {meal_data['protein']}g\n"
            f"🍞 Carbs: {meal_data['carbs']}g\n"
            f"🥑 Fat: {meal_data['fat']}g\n"
            f"🌾 Fiber: {meal_data['fiber']}g\n"
            f"🍬 Sugar: {meal_data['sugar']}g\n\n"
            f"💡 *AI Usage*\n"
            f"📊 Tokens: {usage['total_tokens']:,} (in: {usage['prompt_tokens']:,}, out: {usage['output_tokens']:,})\n"
            f"💰 Cost: ${usage['cost_usd']:.6f}\n\n"
            f"Save this meal?"
        )

        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    except sr.UnknownValueError:
        logger.error(f"Speech recognition could not understand audio for user {user_id}")
        await update.message.reply_text(t('error_voice_unclear', lang))
    except sr.RequestError as e:
        logger.error(f"Speech recognition service error for user {user_id}: {e}")
        await update.message.reply_text(t('error_voice_service', lang))
    except Exception as e:
        logger.error(f"Error processing voice for user {user_id}: {e}", exc_info=True)
        await update.message.reply_text(t('error_voice_generic', lang, error=str(e)))


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    user_id = update.effective_user.id
    text = update.message.text

    # Check if user exists
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text(
            "Please complete onboarding first with /start"
        )
        return

    # Check if we're awaiting a calorie edit
    if context.user_data.get('awaiting_calorie_edit'):
        context.user_data['awaiting_calorie_edit'] = False

        # Get pending meal
        meal = db.get_pending_meal(user_id)

        if not meal:
            await update.message.reply_text("❌ No pending meal found. Please send a new photo or voice message.")
            return

        # Try to extract calorie value or use AI to re-analyze with user feedback
        import re
        calorie_match = re.search(r'(\d+)\s*(?:kcal)?', text, re.IGNORECASE)

        if calorie_match:
            # User provided a simple number
            new_calories = int(calorie_match.group(1))
            old_calories = meal['calories']

            # Recalculate macros proportionally
            if old_calories > 0:
                ratio = new_calories / old_calories
                meal['protein'] = round(meal['protein'] * ratio, 1)
                meal['carbs'] = round(meal['carbs'] * ratio, 1)
                meal['fat'] = round(meal['fat'] * ratio, 1)
                meal['fiber'] = round(meal['fiber'] * ratio, 1)
                meal['sugar'] = round(meal['sugar'] * ratio, 1)

            # Update calories
            meal['calories'] = new_calories

            # Update pending meal
            db.save_pending_meal(user_id, meal)

            keyboard = [
                [InlineKeyboardButton("✅ Save", callback_data="save_meal")],
                [InlineKeyboardButton("✏️ Edit Again", callback_data="edit_calories")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_meal")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            message = f"✅ *Updated Nutritional Information:*\n\n"
            message += f"🍽 {meal['description']}\n"
            message += f"🍴 Meal Type: {meal['meal_type'].title()}\n\n"
            message += f"⚡️ Calories: {meal['calories']} kcal\n"
            message += f"🥩 Protein: {meal['protein']}g\n"
            message += f"🍞 Carbs: {meal['carbs']}g\n"
            message += f"🥑 Fat: {meal['fat']}g\n"
            message += f"🌾 Fiber: {meal['fiber']}g\n"
            message += f"🍬 Sugar: {meal['sugar']}g\n\n"
            message += f"Save this meal?"

            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return
        else:
            # User provided description/correction - use AI to re-analyze
            await update.message.reply_text("🔍 Re-analyzing with your feedback...")

            try:
                # Use user's API key if they have one
                if user.get('gemini_api_key'):
                    user_ai = AIAnalyzer(api_key=user['gemini_api_key'])
                    correction_prompt = f"Original meal: {meal['description']}\nUser correction: {text}\n\nProvide updated nutritional information."
                    updated_meal, usage = user_ai.analyze_text_meal(correction_prompt)
                else:
                    correction_prompt = f"Original meal: {meal['description']}\nUser correction: {text}\n\nProvide updated nutritional information."
                    updated_meal, usage = ai.analyze_text_meal(correction_prompt)

                # Preserve image path and update description
                updated_meal['image_path'] = meal.get('image_path')
                updated_meal['description'] = f"{meal['description']} (corrected: {text})"

                # Update pending meal
                db.save_pending_meal(user_id, updated_meal)

                keyboard = [
                    [InlineKeyboardButton("✅ Save", callback_data="save_meal")],
                    [InlineKeyboardButton("✏️ Edit Again", callback_data="edit_calories")],
                    [InlineKeyboardButton("❌ Cancel", callback_data="cancel_meal")],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                message = f"✅ *Updated Nutritional Information:*\n\n"
                message += f"🍽 {updated_meal['description']}\n"
                message += f"🍴 Meal Type: {updated_meal['meal_type'].title()}\n\n"
                message += f"⚡️ Calories: {updated_meal['calories']} kcal\n"
                message += f"🥩 Protein: {updated_meal['protein']}g\n"
                message += f"🍞 Carbs: {updated_meal['carbs']}g\n"
                message += f"🥑 Fat: {updated_meal['fat']}g\n"
                message += f"🌾 Fiber: {updated_meal['fiber']}g\n"
                message += f"🍬 Sugar: {updated_meal['sugar']}g\n\n"
                message += f"💡 AI Usage: {usage['total_tokens']:,} tokens (${usage['cost_usd']:.6f})\n\n"
                message += f"Save this meal?"

                await update.message.reply_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                return
            except Exception as e:
                logger.error(f"Error re-analyzing meal: {e}")
                await update.message.reply_text(
                    "❌ Sorry, I couldn't re-analyze the meal. Please try entering just a calorie number."
                )
                return

    # Use AI to understand user intent
    intent = ai.parse_user_intent(text, user)

    # Check if user is approved or has own API key (allow read-only actions)
    if not user.get('is_approved') and not user.get('gemini_api_key'):
        # Allow get_stats and get_profile without approval
        if intent['action'] not in ['get_stats', 'get_profile']:
            await update.message.reply_text(
                "⏳ Your account is pending approval.\n\n"
                "You cannot log meals or update settings until approved.\n\n"
                "Please wait for admin approval, or restart onboarding with /start to provide your own Gemini API key.\n\n"
                "You can still view your profile with commands like /profile or /help."
            )
            return

    # Handle different intents
    if intent['action'] == 'get_stats':
        # Get stats based on AI-determined period
        period = intent.get('period', 'day')

        now = datetime.now()
        if period == 'day':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            period_name = "Today"
        elif period == 'week':
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
            period_name = "This Week"
        elif period == 'month':
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                end = start.replace(year=now.year+1, month=1)
            else:
                end = start.replace(month=now.month+1)
            period_name = "This Month"
        elif period == 'year':
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start.replace(year=now.year+1)
            period_name = "This Year"
        else:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            period_name = "Today"

        stats = db.get_stats(user_id, start, end)

        if not stats or stats['meal_count'] == 0:
            await update.message.reply_text(f"No meals recorded for {period_name.lower()}.")
            return

        total_cals = stats['total_calories'] or 0
        total_protein = stats['total_protein'] or 0
        total_carbs = stats['total_carbs'] or 0
        total_fat = stats['total_fat'] or 0
        total_fiber = stats['total_fiber'] or 0
        total_sugar = stats['total_sugar'] or 0
        avg_cals = stats['avg_calories'] or 0
        meal_count = stats['meal_count']

        message = (
            f"📊 *{period_name} Statistics*\n\n"
            f"🍽 Meals logged: {meal_count}\n"
            f"⚡️ Total calories: {int(total_cals)} kcal\n"
            f"📈 Average per meal: {int(avg_cals)} kcal\n\n"
            f"*Macros:*\n"
            f"🥩 Protein: {int(total_protein)}g\n"
            f"🍞 Carbs: {int(total_carbs)}g\n"
            f"🥑 Fat: {int(total_fat)}g\n"
            f"🌾 Fiber: {int(total_fiber)}g\n"
            f"🍬 Sugar: {int(total_sugar)}g\n\n"
        )

        if period == 'day':
            target = user['daily_calorie_target']
            remaining = target - total_cals
            message += f"🎯 Daily target: {int(target)} kcal\n"
            message += f"📊 Remaining: {int(remaining)} kcal"

        await update.message.reply_text(message, parse_mode='Markdown')
        return

    elif intent['action'] == 'get_profile':
        # Show user profile
        message = (
            f"👤 *Your Profile*\n\n"
            f"📛 Name: {user['name']}\n"
            f"📏 Height: {user['height']} cm\n"
            f"⚖️ Weight: {user['weight']} kg\n"
            f"🎯 Goal: {user['goal'].replace('_', ' ').title()}\n"
            f"⚡️ Goal Speed: {user['goal_speed'].title()}\n"
            f"🍽 Daily Calorie Target: {int(user['daily_calorie_target'])} kcal\n\n"
        )

        meal_times = db.get_meal_times(user_id)
        if meal_times:
            message += "🔔 *Meal Reminders:*\n"
            for meal_type, meal_time in meal_times.items():
                message += f"• {meal_type.title()}: {meal_time}\n"

        await update.message.reply_text(message, parse_mode='Markdown')
        return

    elif intent['action'] == 'update_setting' and intent['confidence'] > 0.7:
        field = intent['field']
        value = intent['value']

        # Update user setting
        if field == 'weight':
            db.update_user(user_id, weight=value)
            # Recalculate calorie target
            new_target = calculate_daily_calorie_target(
                weight=value,
                height=user['height'],
                goal=user['goal'],
                goal_speed=user['goal_speed']
            )
            db.update_user(user_id, daily_calorie_target=new_target)
            await update.message.reply_text(
                f"✅ Updated weight to {value}kg\n"
                f"📊 New daily calorie target: {new_target} kcal"
            )
        elif field == 'height':
            db.update_user(user_id, height=value)
            new_target = calculate_daily_calorie_target(
                weight=user['weight'],
                height=value,
                goal=user['goal'],
                goal_speed=user['goal_speed']
            )
            db.update_user(user_id, daily_calorie_target=new_target)
            await update.message.reply_text(
                f"✅ Updated height to {value}cm\n"
                f"📊 New daily calorie target: {new_target} kcal"
            )
        elif field == 'goal':
            db.update_user(user_id, goal=value)
            new_target = calculate_daily_calorie_target(
                weight=user['weight'],
                height=user['height'],
                goal=value,
                goal_speed=user['goal_speed']
            )
            db.update_user(user_id, daily_calorie_target=new_target)
            await update.message.reply_text(
                f"✅ Updated goal to {value.replace('_', ' ')}\n"
                f"📊 New daily calorie target: {new_target} kcal"
            )
        elif field == 'goal_speed':
            db.update_user(user_id, goal_speed=value)
            new_target = calculate_daily_calorie_target(
                weight=user['weight'],
                height=user['height'],
                goal=user['goal'],
                goal_speed=value
            )
            db.update_user(user_id, daily_calorie_target=new_target)
            await update.message.reply_text(
                f"✅ Updated goal speed to {value}\n"
                f"📊 New daily calorie target: {new_target} kcal"
            )
        return

    elif intent['action'] == 'update_meal_time' and intent['confidence'] > 0.7:
        field = intent['field']
        value = intent['value']

        meal_type = field.replace('_time', '')
        db.set_meal_time(user_id, meal_type, value)
        await update.message.reply_text(
            f"✅ Updated {meal_type} reminder to {value}"
        )
        return

    elif intent['action'] == 'log_meal':
        # Treat as meal description
        await update.message.reply_text("🔍 Analyzing your meal...")

        try:
            meal_data, usage = ai.analyze_text_meal(text)

            # Ensure meal_type is set (fallback to 'snack' if not provided)
            if 'meal_type' not in meal_data or not meal_data['meal_type']:
                meal_data['meal_type'] = 'snack'

            # Save to pending meals
            db.save_pending_meal(user_id, meal_data)

            # Send results with save/edit/cancel buttons
            keyboard = [
                [InlineKeyboardButton("✅ Save", callback_data="save_meal")],
                [InlineKeyboardButton("✏️ Edit Calories", callback_data="edit_calories")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_meal")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            message = (
                f"📊 *Nutritional Information:*\n\n"
                f"🍽 {meal_data['description']}\n"
                f"🍴 Meal Type: {meal_data['meal_type'].title()}\n\n"
                f"⚡️ Calories: {meal_data['calories']} kcal\n"
                f"🥩 Protein: {meal_data['protein']}g\n"
                f"🍞 Carbs: {meal_data['carbs']}g\n"
                f"🥑 Fat: {meal_data['fat']}g\n"
                f"🌾 Fiber: {meal_data['fiber']}g\n"
                f"🍬 Sugar: {meal_data['sugar']}g\n\n"
                f"💡 *AI Usage*\n"
                f"📊 Tokens: {usage['total_tokens']:,} (in: {usage['prompt_tokens']:,}, out: {usage['output_tokens']:,})\n"
                f"💰 Cost: ${usage['cost_usd']:.6f}\n\n"
                f"Save this meal?"
            )

            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            await update.message.reply_text(
                "❌ Sorry, I couldn't understand that. Try:\n"
                "• Sending a photo of your meal\n"
                "• Describing your meal in detail\n"
                "• Asking for stats: 'show my stats'\n"
                "• Asking about your profile: 'what's my info?'\n"
                "• Updating settings: 'change my weight to 75kg'"
            )
    else:
        # Default: assume they want to log a meal
        await update.message.reply_text("🔍 Analyzing your meal...")

        try:
            meal_data, usage = ai.analyze_text_meal(text)

            # Save to pending meals
            db.save_pending_meal(user_id, meal_data)

            # Send results with save/cancel buttons
            keyboard = [
                [InlineKeyboardButton("✅ Save", callback_data="save_meal")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_meal")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            message = (
                f"📊 *Nutritional Information:*\n\n"
                f"🍽 {meal_data['description']}\n"
                f"🍴 Meal Type: {meal_data['meal_type'].title()}\n\n"
                f"⚡️ Calories: {meal_data['calories']} kcal\n"
                f"🥩 Protein: {meal_data['protein']}g\n"
                f"🍞 Carbs: {meal_data['carbs']}g\n"
                f"🥑 Fat: {meal_data['fat']}g\n"
                f"🌾 Fiber: {meal_data['fiber']}g\n"
                f"🍬 Sugar: {meal_data['sugar']}g\n\n"
                f"💡 *AI Usage*\n"
                f"📊 Tokens: {usage['total_tokens']:,} (in: {usage['prompt_tokens']:,}, out: {usage['output_tokens']:,})\n"
                f"💰 Cost: ${usage['cost_usd']:.6f}\n\n"
                f"Save this meal?"
            )

            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            await update.message.reply_text(
                "❌ Sorry, I couldn't understand that. Try:\n"
                "• Sending a photo of your meal\n"
                "• Describing your meal in detail\n"
                "• Asking for stats: 'show my stats'\n"
                "• Asking about your profile: 'what's my info?'\n"
                "• Updating settings: 'change my weight to 75kg'"
            )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == 'save_meal':
        # Get pending meal
        meal = db.get_pending_meal(user_id)

        if meal:
            # Save to meals
            db.save_meal(user_id, meal)
            db.delete_pending_meal(user_id)

            # Remove buttons from the original prediction message (without editing its text)
            try:
                await query.edit_message_reply_markup(reply_markup=None)
            except Exception as e:
                logger.warning(f"Failed to clear inline buttons: {e}")

            # Get user's daily progress
            user = db.get_user(user_id)
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)

            stats = db.get_stats(user_id, today_start, today_end)
            meals_today = db.get_meals_by_date_range(user_id, today_start, today_end)

            total_cals = stats['total_calories'] or 0
            remaining = user['daily_calorie_target'] - total_cals
            percentage = (total_cals / user['daily_calorie_target'] * 100) if user['daily_calorie_target'] > 0 else 0

            # Progress bar
            bar_length = 20
            filled = int(bar_length * percentage / 100)
            bar = "█" * filled + "░" * (bar_length - filled)

            message = f"✅ *Meal Saved!*\n\n"
            message += f"📊 *TODAY'S PROGRESS*\n"
            message += f"{bar} {percentage:.1f}%\n\n"
            message += f"⚡️ {int(total_cals)} / {int(user['daily_calorie_target'])} kcal\n"
            message += f"📊 Remaining: {int(remaining)} kcal\n\n"
            message += f"*MACROS TODAY:*\n"
            message += f"🥩 Protein: {int(stats['total_protein'] or 0)}g\n"
            message += f"🍞 Carbs: {int(stats['total_carbs'] or 0)}g\n"
            message += f"🥑 Fat: {int(stats['total_fat'] or 0)}g\n\n"
            message += f"🍽 Meals today: {len(meals_today)}"

            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=message,
                parse_mode='Markdown',
            )
        else:
            await query.edit_message_text("❌ No pending meal found.")

    elif query.data == 'cancel_meal':
        db.delete_pending_meal(user_id)
        await query.edit_message_text("❌ Meal cancelled.")

    elif query.data == 'edit_calories':
        # Get pending meal
        meal = db.get_pending_meal(user_id)

        if meal:
            await query.edit_message_text(
                f"Current calories: *{meal['calories']} kcal*\n\n"
                f"Please send the corrected calorie value.\n\n"
                f"You can also mention:\n"
                f"• What's in the photo if AI missed something\n"
                f"• Portion size if different (e.g., 'actually 200g chicken')\n\n"
                f"Examples:\n"
                f"• 450\n"
                f"• 450 kcal\n"
                f"• It's 300g chicken breast not 150g",
                parse_mode='Markdown'
            )
            # Store that we're waiting for calorie edit
            context.user_data['awaiting_calorie_edit'] = True
        else:
            await query.edit_message_text("❌ No pending meal found.")

    elif query.data == 'confirm_reset':
        # Delete all user data
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM meals WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM meal_times WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM pending_meals WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()

        await query.edit_message_text(
            "✅ All data has been reset.\n\n"
            "Use /start to set up your profile again."
        )

    elif query.data == 'cancel_reset':
        await query.edit_message_text("❌ Reset cancelled. Your data is safe.")

    elif query.data.startswith('lang_'):
        # Language selection
        lang_code = query.data.split('_')[1]  # Extract 'en', 'ro', or 'ru'

        # Update user language
        db.update_user(user_id, language=lang_code)

        # Get confirmation message in the new language
        await query.edit_message_text(t('language_changed', lang_code))


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show statistics"""
    user_id = update.effective_user.id

    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("Please complete onboarding first with /start")
        return

    # Get period from command args
    args = context.args
    period = args[0] if args else 'day'

    now = datetime.now()

    if period == 'day':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        period_name = "Today"
    elif period == 'week':
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
        period_name = "This Week"
    elif period == 'month':
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            end = start.replace(year=now.year+1, month=1)
        else:
            end = start.replace(month=now.month+1)
        period_name = "This Month"
    elif period == 'year':
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = start.replace(year=now.year+1)
        period_name = "This Year"
    else:
        await update.message.reply_text(
            "Usage: /stats [day|week|month|year]\n"
            "Example: /stats week"
        )
        return

    stats = db.get_stats(user_id, start, end)

    if not stats or stats['meal_count'] == 0:
        await update.message.reply_text(f"No meals recorded for {period_name.lower()}.")
        return

    total_cals = stats['total_calories'] or 0
    total_protein = stats['total_protein'] or 0
    total_carbs = stats['total_carbs'] or 0
    total_fat = stats['total_fat'] or 0
    total_fiber = stats['total_fiber'] or 0
    total_sugar = stats['total_sugar'] or 0
    avg_cals = stats['avg_calories'] or 0
    meal_count = stats['meal_count']

    message = (
        f"📊 *{period_name} Statistics*\n\n"
        f"🍽 Meals logged: {meal_count}\n"
        f"⚡️ Total calories: {int(total_cals)} kcal\n"
        f"📈 Average per meal: {int(avg_cals)} kcal\n\n"
        f"*Macros:*\n"
        f"🥩 Protein: {int(total_protein)}g\n"
        f"🍞 Carbs: {int(total_carbs)}g\n"
        f"🥑 Fat: {int(total_fat)}g\n"
        f"🌾 Fiber: {int(total_fiber)}g\n"
        f"🍬 Sugar: {int(total_sugar)}g\n\n"
    )

    if period == 'day':
        target = user['daily_calorie_target']
        remaining = target - total_cals
        message += f"🎯 Daily target: {int(target)} kcal\n"
        message += f"📊 Remaining: {int(remaining)} kcal"

    await update.message.reply_text(message, parse_mode='Markdown')


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show today's statistics"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("Please complete onboarding first with /start")
        return

    now = datetime.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    stats = db.get_stats(user_id, start, end)

    if not stats or stats['meal_count'] == 0:
        await update.message.reply_text("No meals recorded today.")
        return

    total_cals = stats['total_calories'] or 0
    target = user['daily_calorie_target']
    remaining = target - total_cals

    message = (
        f"📊 *Today's Statistics*\n\n"
        f"🍽 Meals logged: {stats['meal_count']}\n"
        f"⚡️ Calories: {int(total_cals)} / {int(target)} kcal\n"
        f"📊 Remaining: {int(remaining)} kcal\n\n"
        f"*Macros:*\n"
        f"🥩 Protein: {int(stats['total_protein'] or 0)}g\n"
        f"🍞 Carbs: {int(stats['total_carbs'] or 0)}g\n"
        f"🥑 Fat: {int(stats['total_fat'] or 0)}g\n"
        f"🌾 Fiber: {int(stats['total_fiber'] or 0)}g\n"
        f"🍬 Sugar: {int(stats['total_sugar'] or 0)}g"
    )

    await update.message.reply_text(message, parse_mode='Markdown')


async def week_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show this week's statistics"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("Please complete onboarding first with /start")
        return

    now = datetime.now()
    start = now - timedelta(days=now.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=7)

    stats = db.get_stats(user_id, start, end)

    if not stats or stats['meal_count'] == 0:
        await update.message.reply_text("No meals recorded this week.")
        return

    message = (
        f"📊 *This Week's Statistics*\n\n"
        f"🍽 Meals logged: {stats['meal_count']}\n"
        f"⚡️ Total calories: {int(stats['total_calories'] or 0)} kcal\n"
        f"📈 Avg per meal: {int(stats['avg_calories'] or 0)} kcal\n\n"
        f"*Macros:*\n"
        f"🥩 Protein: {int(stats['total_protein'] or 0)}g\n"
        f"🍞 Carbs: {int(stats['total_carbs'] or 0)}g\n"
        f"🥑 Fat: {int(stats['total_fat'] or 0)}g\n"
        f"🌾 Fiber: {int(stats['total_fiber'] or 0)}g\n"
        f"🍬 Sugar: {int(stats['total_sugar'] or 0)}g"
    )

    await update.message.reply_text(message, parse_mode='Markdown')


async def month_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show this month's statistics"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("Please complete onboarding first with /start")
        return

    now = datetime.now()
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 12:
        end = start.replace(year=now.year+1, month=1)
    else:
        end = start.replace(month=now.month+1)

    stats = db.get_stats(user_id, start, end)

    if not stats or stats['meal_count'] == 0:
        await update.message.reply_text("No meals recorded this month.")
        return

    message = (
        f"📊 *This Month's Statistics*\n\n"
        f"🍽 Meals logged: {stats['meal_count']}\n"
        f"⚡️ Total calories: {int(stats['total_calories'] or 0)} kcal\n"
        f"📈 Avg per meal: {int(stats['avg_calories'] or 0)} kcal\n\n"
        f"*Macros:*\n"
        f"🥩 Protein: {int(stats['total_protein'] or 0)}g\n"
        f"🍞 Carbs: {int(stats['total_carbs'] or 0)}g\n"
        f"🥑 Fat: {int(stats['total_fat'] or 0)}g\n"
        f"🌾 Fiber: {int(stats['total_fiber'] or 0)}g\n"
        f"🍬 Sugar: {int(stats['total_sugar'] or 0)}g"
    )

    await update.message.reply_text(message, parse_mode='Markdown')


async def year_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show this year's statistics"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("Please complete onboarding first with /start")
        return

    now = datetime.now()
    start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    end = start.replace(year=now.year+1)

    stats = db.get_stats(user_id, start, end)

    if not stats or stats['meal_count'] == 0:
        await update.message.reply_text("No meals recorded this year.")
        return

    message = (
        f"📊 *This Year's Statistics*\n\n"
        f"🍽 Meals logged: {stats['meal_count']}\n"
        f"⚡️ Total calories: {int(stats['total_calories'] or 0)} kcal\n"
        f"📈 Avg per meal: {int(stats['avg_calories'] or 0)} kcal\n\n"
        f"*Macros:*\n"
        f"🥩 Protein: {int(stats['total_protein'] or 0)}g\n"
        f"🍞 Carbs: {int(stats['total_carbs'] or 0)}g\n"
        f"🥑 Fat: {int(stats['total_fat'] or 0)}g\n"
        f"🌾 Fiber: {int(stats['total_fiber'] or 0)}g\n"
        f"🍬 Sugar: {int(stats['total_sugar'] or 0)}g"
    )

    await update.message.reply_text(message, parse_mode='Markdown')


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user profile"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("Please complete onboarding first with /start")
        return

    message = (
        f"👤 *Your Profile*\n\n"
        f"📛 Name: {user['name']}\n"
        f"📏 Height: {user['height']} cm\n"
        f"⚖️ Weight: {user['weight']} kg\n"
        f"🎯 Goal: {user['goal'].replace('_', ' ').title()}\n"
        f"⚡️ Goal Speed: {user['goal_speed'].title()}\n"
        f"🍽 Daily Calorie Target: {int(user['daily_calorie_target'])} kcal\n\n"
    )

    meal_times = db.get_meal_times(user_id)
    if meal_times:
        message += "🔔 *Meal Reminders:*\n"
        for meal_type, meal_time in meal_times.items():
            message += f"• {meal_type.title()}: {meal_time}\n"

    await update.message.reply_text(message, parse_mode='Markdown')


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent meal history"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("Please complete onboarding first with /start")
        return

    now = datetime.now()
    start = now - timedelta(days=7)

    meals = db.get_meals_by_date_range(user_id, start, now)

    if not meals:
        await update.message.reply_text("No recent meals found.")
        return

    message = "📜 *Recent Meals (Last 7 Days)*\n\n"

    for meal in meals[:10]:  # Show last 10 meals
        eaten_at = datetime.fromisoformat(meal['eaten_at'])
        message += (
            f"🍽 {meal['description'][:40]}...\n"
            f"   ⚡️ {int(meal['calories'])} kcal | "
            f"🥩 {int(meal['protein'])}g | "
            f"🍞 {int(meal['carbs'])}g\n"
            f"   📅 {eaten_at.strftime('%b %d, %I:%M %p')}\n\n"
        )

    if len(meals) > 10:
        message += f"_...and {len(meals) - 10} more meals_"

    await update.message.reply_text(message, parse_mode='Markdown')


async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete last logged meal"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("Please complete onboarding first with /start")
        return

    # Get most recent meal
    now = datetime.now()
    start = now - timedelta(days=1)
    meals = db.get_meals_by_date_range(user_id, start, now)

    if not meals:
        await update.message.reply_text("No recent meals to delete.")
        return

    # Delete the most recent meal
    last_meal = meals[0]
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM meals WHERE id = ?', (last_meal['id'],))
    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"✅ Deleted last meal:\n"
        f"{last_meal['description']}\n"
        f"({int(last_meal['calories'])} kcal)"
    )


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset user data and start over"""
    user_id = update.effective_user.id

    keyboard = [
        [InlineKeyboardButton("✅ Yes, reset everything", callback_data="confirm_reset")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_reset")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "⚠️ *Warning*\n\n"
        "This will delete all your data:\n"
        "• Profile settings\n"
        "• All logged meals\n"
        "• Meal reminders\n\n"
        "Are you sure?",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show progress towards daily goal"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("Please complete onboarding first with /start")
        return

    now = datetime.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    stats = db.get_stats(user_id, start, end)

    total_cals = stats['total_calories'] or 0 if stats else 0
    target = user['daily_calorie_target']
    remaining = target - total_cals
    percentage = (total_cals / target * 100) if target > 0 else 0

    # Create progress bar
    bar_length = 20
    filled = int(bar_length * percentage / 100)
    bar = "█" * filled + "░" * (bar_length - filled)

    message = (
        f"📈 *Daily Progress*\n\n"
        f"{bar} {percentage:.1f}%\n\n"
        f"⚡️ Consumed: {int(total_cals)} kcal\n"
        f"🎯 Target: {int(target)} kcal\n"
        f"📊 Remaining: {int(remaining)} kcal\n\n"
    )

    if remaining < 0:
        message += f"⚠️ You're {int(abs(remaining))} kcal over your target!"
    elif remaining < 200:
        message += "✅ Almost there! Great job!"
    else:
        message += f"💪 Keep going! {int(remaining)} kcal to go!"

    await update.message.reply_text(message, parse_mode='Markdown')


async def reminders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show and manage meal reminders"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("Please complete onboarding first with /start")
        return

    meal_times = db.get_meal_times(user_id)

    if not meal_times:
        await update.message.reply_text(
            "No meal reminders set.\n\n"
            "Set them with commands like:\n"
            "• Set breakfast reminder to 8am\n"
            "• Update lunch time to 1pm"
        )
        return

    message = "🔔 *Your Meal Reminders*\n\n"
    for meal_type, meal_time in meal_times.items():
        message += f"• {meal_type.title()}: {meal_time}\n"

    message += (
        "\n💡 *Change reminders:*\n"
        "Just type naturally:\n"
        "• 'Set breakfast to 7:30am'\n"
        "• 'Change lunch time to 12:30'"
    )

    await update.message.reply_text(message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    help_text = (
        "🤖 *Calorie Tracker Bot Help*\n\n"
        "*📸 Tracking Meals:*\n"
        "• Send a photo of your meal\n"
        "• Send a voice message\n"
        "• Type a meal description\n\n"
        "*⚡️ Quick Commands:*\n"
        "/today - Today's stats\n"
        "/week - This week's stats\n"
        "/month - This month's stats\n"
        "/year - This year's stats\n"
        "/yesterday - Yesterday's stats (Instagram-ready)\n"
        "/progress - Daily progress bar\n"
        "/profile - Your profile info\n"
        "/history - Recent meals\n"
        "/reminders - Meal reminders\n"
        "/delete - Delete last meal\n"
        "/reset - Reset all data\n"
        "/help - Show this message\n\n"
        "*💬 Natural Language:*\n"
        "Just type naturally:\n"
        "• 'Show my stats'\n"
        "• 'What's my weight?'\n"
        "• 'Change my weight to 75kg'\n"
        "• 'Set breakfast to 8am'"
    )

    await update.message.reply_text(help_text, parse_mode='Markdown')


async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Language selection command"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)

    if not user:
        await update.message.reply_text("Please complete onboarding first with /start")
        return

    # Create language selection keyboard
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇷🇴 Română", callback_data="lang_ro")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    lang = get_user_lang(user)
    await update.message.reply_text(
        t('select_language', lang),
        reply_markup=reply_markup
    )


async def yesterday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show yesterday's stats in Instagram-ready format"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("Please complete onboarding first with /start")
        return

    # Get yesterday's date range
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today - timedelta(days=1)
    yesterday_end = today

    stats = db.get_stats(user_id, yesterday_start, yesterday_end)
    meals = db.get_meals_by_date_range(user_id, yesterday_start, yesterday_end)

    if not stats or stats['meal_count'] == 0:
        await update.message.reply_text("No meals recorded yesterday.")
        return

    # Group meals by type
    breakfast_meals = [m for m in meals if m['meal_type'] == 'breakfast']
    lunch_meals = [m for m in meals if m['meal_type'] == 'lunch']
    dinner_meals = [m for m in meals if m['meal_type'] == 'dinner']
    snack_meals = [m for m in meals if m['meal_type'] == 'snack']

    # Create Instagram-ready message
    date_str = yesterday_start.strftime('%B %d, %Y')

    message = f"📅 *{date_str}*\n"
    message += "=" * 30 + "\n\n"

    # Total summary
    message += f"📊 *DAILY SUMMARY*\n"
    message += f"⚡️ Total Calories: {int(stats['total_calories'] or 0)} kcal\n"
    message += f"🍽 Meals Logged: {stats['meal_count']}\n\n"

    # Macros
    message += f"*MACROS:*\n"
    message += f"🥩 Protein: {int(stats['total_protein'] or 0)}g\n"
    message += f"🍞 Carbs: {int(stats['total_carbs'] or 0)}g\n"
    message += f"🥑 Fat: {int(stats['total_fat'] or 0)}g\n"
    message += f"🌾 Fiber: {int(stats['total_fiber'] or 0)}g\n\n"

    # Meals breakdown
    if breakfast_meals:
        message += f"🌅 *BREAKFAST* ({len(breakfast_meals)} meal{'s' if len(breakfast_meals) > 1 else ''})\\n"
        for meal in breakfast_meals:
            message += f"   • {meal['description'][:40]}... ({int(meal['calories'])} kcal)\n"
        message += "\n"

    if lunch_meals:
        message += f"🌞 *LUNCH* ({len(lunch_meals)} meal{'s' if len(lunch_meals) > 1 else ''})\\n"
        for meal in lunch_meals:
            message += f"   • {meal['description'][:40]}... ({int(meal['calories'])} kcal)\n"
        message += "\n"

    if dinner_meals:
        message += f"🌙 *DINNER* ({len(dinner_meals)} meal{'s' if len(dinner_meals) > 1 else ''})\\n"
        for meal in dinner_meals:
            message += f"   • {meal['description'][:40]}... ({int(meal['calories'])} kcal)\n"
        message += "\n"

    if snack_meals:
        message += f"🍿 *SNACKS* ({len(snack_meals)} snack{'s' if len(snack_meals) > 1 else ''})\\n"
        for meal in snack_meals:
            message += f"   • {meal['description'][:40]}... ({int(meal['calories'])} kcal)\n"
        message += "\n"

    message += "=" * 30 + "\n"
    message += f"🎯 Target: {int(user['daily_calorie_target'])} kcal\n"

    difference = (stats['total_calories'] or 0) - user['daily_calorie_target']
    if difference > 0:
        message += f"📈 Over by: {int(difference)} kcal"
    else:
        message += f"📉 Under by: {int(abs(difference))} kcal"

    await update.message.reply_text(message, parse_mode='Markdown')


async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to approve users"""
    user_id = update.effective_user.id

    # Check if admin
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ This command is only available to administrators.")
        return

    # Get username from command args
    if not context.args:
        await update.message.reply_text(
            "Usage: /approve @username\n"
            "Example: /approve @john"
        )
        return

    username = context.args[0].replace('@', '')

    # Find user by username
    target_user = db.get_user_by_username(username)

    if not target_user:
        await update.message.reply_text(f"❌ User @{username} not found.")
        return

    # Approve user
    db.approve_user(target_user['user_id'])

    # Send confirmation to admin
    await update.message.reply_text(
        f"✅ User @{username} has been approved!\n"
        f"They can now use the bot without providing their own API key."
    )

    # Send notification to the approved user
    try:
        await context.bot.send_message(
            chat_id=target_user['user_id'],
            text=f"🎉 *Congratulations!*\n\n"
                 f"Your account has been approved by the admin.\n"
                 f"You can now use the bot to track your meals!\n\n"
                 f"Send a photo of your meal to get started.",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ User approved but couldn't send notification: {str(e)}")


async def approve_index_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin shortcut: /approve_1, /approve_2, ... approves pending users by index from /seealluserstats list."""
    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ This command is only available to administrators.")
        return

    text = (update.message.text or "").strip()
    m = re.match(r"^/approve_(\d+)\b", text)
    if not m:
        await update.message.reply_text("Usage: /approve_1 (from /seealluserstats pending list)")
        return

    idx = int(m.group(1))
    users = db.get_all_users()

    pending = [
        u for u in users
        if u.get('is_approved', 0) != 1 and not u.get('gemini_api_key')
    ]

    if idx < 1 or idx > len(pending):
        await update.message.reply_text(f"❌ Invalid index. Pending users: {len(pending)}")
        return

    target_user = pending[idx - 1]
    username = target_user.get('username', 'unknown')
    if username.startswith('@'):
        username = username[1:]

    db.approve_user(target_user['user_id'])

    await update.message.reply_text(
        f"✅ Approved #{idx}: @{username} ({target_user.get('name', '')})"
    )

    try:
        await context.bot.send_message(
            chat_id=target_user['user_id'],
            text=f"🎉 *Congratulations!*\n\n"
                 f"Your account has been approved by the admin.\n"
                 f"You can now use the bot to track your meals!\n\n"
                 f"Send a photo of your meal to get started.",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ User approved but couldn't send notification: {str(e)}")


async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin debug command to see recent user profiles
    Usage: /debug [weight=65] [name=john] [approved=0]
    """
    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ This command is only available to administrators.")
        return

    users = db.get_all_users()

    if not users:
        await update.message.reply_text("No users found in database.")
        return

    # Parse filter arguments
    args = context.args
    filtered_users = users

    if args:
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                key = key.lower().strip()
                value = value.strip()

                if key == 'weight':
                    try:
                        weight_filter = float(value)
                        filtered_users = [u for u in filtered_users if u.get('weight') == weight_filter]
                    except ValueError:
                        pass
                elif key == 'height':
                    try:
                        height_filter = float(value)
                        filtered_users = [u for u in filtered_users if u.get('height') == height_filter]
                    except ValueError:
                        pass
                elif key == 'name':
                    filtered_users = [u for u in filtered_users if value.lower() in (u.get('name', '') or '').lower()]
                elif key == 'approved':
                    approved_filter = 1 if value.lower() in ['1', 'true', 'yes'] else 0
                    filtered_users = [u for u in filtered_users if u.get('is_approved', 0) == approved_filter]
                elif key == 'id':
                    try:
                        id_filter = int(value)
                        filtered_users = [u for u in filtered_users if u.get('user_id') == id_filter]
                    except ValueError:
                        pass

    # Sort by created_at descending (newest first) and limit to 10
    sorted_users = sorted(filtered_users, key=lambda u: u.get('created_at', ''), reverse=True)[:10]

    if not sorted_users:
        await update.message.reply_text("No users found matching the filters.")
        return

    filter_text = f" (Filters: {' '.join(args)})" if args else ""
    message = f"🔍 *DEBUG - Users{filter_text}*\n"
    message += f"Found: {len(filtered_users)} | Showing: {len(sorted_users)}\n\n"

    for i, user in enumerate(sorted_users, 1):
        user_id_val = user.get('user_id', 'N/A')
        username = user.get('username', None)
        name = user.get('name', 'N/A')
        height = user.get('height', 'N/A')
        weight = user.get('weight', 'N/A')
        is_approved = user.get('is_approved', 0)
        has_api_key = 'Yes' if user.get('gemini_api_key') else 'No'
        created = user.get('created_at', 'N/A')

        # Handle missing username
        username_display = f"@{username}" if username else "NO USERNAME"

        message += f"{i}. *User ID:* {user_id_val}\n"
        message += f"   Username: {username_display}\n"
        message += f"   Name: {name}\n"
        message += f"   Height: {height} cm\n"
        message += f"   Weight: {weight} kg\n"
        message += f"   Approved: {'✅' if is_approved == 1 else '❌'}\n"
        message += f"   Has API Key: {has_api_key}\n"
        message += f"   Created: {created}\n\n"

    await update.message.reply_text(message, parse_mode='Markdown')


async def seealluserstats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to see all user statistics"""
    user_id = update.effective_user.id

    # Check if admin
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ This command is only available to administrators.")
        return

    users = db.get_all_users()

    if not users:
        await update.message.reply_text("No users found.")
        return

    message = "👥 *ALL USERS STATISTICS*\n\n"

    total_users = len(users)
    approved_users = len([u for u in users if u.get('is_approved', 0) == 1])
    own_key_users = len([u for u in users if u.get('gemini_api_key')])
    pending_users = len([u for u in users if u.get('is_approved', 0) != 1 and not u.get('gemini_api_key')])

    message += f"📊 Total Users: {total_users}\n"
    message += f"✅ Approved: {approved_users}\n"
    message += f"🔑 Own API Key: {own_key_users}\n"
    message += f"⏳ Pending: {pending_users}\n\n"

    message += "=" * 30 + "\n\n"

    # Get stats for each user
    now = datetime.now()
    week_start = now - timedelta(days=7)

    pending_approval = [u for u in users if u.get('is_approved', 0) != 1 and not u.get('gemini_api_key')]
    key_users = [u for u in users if u.get('is_approved', 0) != 1 and u.get('gemini_api_key')]
    approved_list = [u for u in users if u.get('is_approved', 0) == 1]

    if pending_approval:
        message += f"⏳ *PENDING APPROVAL* ({len(pending_approval)})\n"
        for i, user in enumerate(pending_approval[:50], start=1):
            username = user.get('username')
            # Handle users without username
            if username:
                if username.startswith('@'):
                    username = username[1:]
                username_display = f"@{username}"
            else:
                username_display = "NO_USERNAME"

            name = user.get('name', '') or ''
            user_id = user.get('user_id', 'unknown')
            message += f"{i}. {username_display} ({name}) [ID:{user_id}] - /approve_{i}\n"
        if len(pending_approval) > 50:
            message += f"...and {len(pending_approval) - 50} more pending\n"
        message += "\n" + "=" * 30 + "\n\n"
    else:
        message += "⏳ *PENDING APPROVAL*: None\n\n"
        message += "=" * 30 + "\n\n"

    # Show first 20 non-pending users (approved + own-key)
    display_users = (approved_list + key_users)[:20]
    for user in display_users:
        username = user.get('username')
        # Handle users without username
        if username:
            if username.startswith('@'):
                username = username[1:]
            username_display = f"@{username}"
        else:
            username_display = "NO_USERNAME"

        name = user.get('name', '') or ''
        user_meals = db.get_meals_by_date_range(user['user_id'], week_start, now)
        meal_count = len(user_meals)

        if user.get('is_approved', 0) == 1:
            status = "✅"
        elif user.get('gemini_api_key'):
            status = "🔑"
        else:
            status = "⏳"

        last_activity = "Never"
        if user_meals:
            last_meal = max(user_meals, key=lambda x: x['eaten_at'])
            last_dt = datetime.fromisoformat(last_meal['eaten_at'])
            days_ago = (now - last_dt).days
            if days_ago == 0:
                last_activity = "Today"
            elif days_ago == 1:
                last_activity = "Yesterday"
            else:
                last_activity = f"{days_ago} days ago"

        message += f"{status} {username_display} ({name})\n"
        message += f"   🍽 Meals (7d): {meal_count}\n"
        message += f"   🔑 Own API: {'✅' if user.get('gemini_api_key') else '❌'}\n"
        message += f"   📅 Last: {last_activity}\n\n"

    remaining = len(approved_list + key_users) - len(display_users)
    if remaining > 0:
        message += f"\n_...and {remaining} more users_"

    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        disable_web_page_preview=True,
    )


def main():
    """Start the bot"""
    # Create application with longer timeouts
    application = (
        Application.builder()
        .token(os.getenv('TELEGRAM_BOT_TOKEN'))
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )

    # Onboarding conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_height)],
            WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_weight)],
            GOAL: [CallbackQueryHandler(get_goal, pattern='^goal_')],
            GOAL_SPEED: [CallbackQueryHandler(get_goal_speed, pattern='^speed_')],
            BREAKFAST_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_breakfast_time)],
            LUNCH_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_lunch_time)],
            DINNER_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_dinner_time)],
            API_KEY: [
                CommandHandler('skip', skip_api_key_command),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_api_key),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_onboarding)],
    )

    application.add_handler(conv_handler)

    # Command handlers
    application.add_handler(CommandHandler('today', today_command))
    application.add_handler(CommandHandler('week', week_command))
    application.add_handler(CommandHandler('month', month_command))
    application.add_handler(CommandHandler('year', year_command))
    application.add_handler(CommandHandler('yesterday', yesterday_command))
    application.add_handler(CommandHandler('profile', profile_command))
    application.add_handler(CommandHandler('history', history_command))
    application.add_handler(CommandHandler('delete', delete_command))
    application.add_handler(CommandHandler('reset', reset_command))
    application.add_handler(CommandHandler('progress', progress_command))
    application.add_handler(CommandHandler('reminders', reminders_command))
    application.add_handler(CommandHandler('stats', stats_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('lang', lang_command))

    # Admin commands
    application.add_handler(CommandHandler('approve', approve_command))
    application.add_handler(CommandHandler('seealluserstats', seealluserstats_command))
    application.add_handler(CommandHandler('debug', debug_command))
    application.add_handler(MessageHandler(filters.Regex(r'^/approve_\d+\b'), approve_index_command))

    # Message handlers
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Button callback handler
    application.add_handler(CallbackQueryHandler(button_callback))

    # Get event loop for scheduler
    import asyncio
    try:
        event_loop = asyncio.get_running_loop()
    except RuntimeError:
        event_loop = asyncio.get_event_loop()

    # Start reminder scheduler with event loop
    scheduler = ReminderScheduler(application.bot, db, event_loop)
    scheduler.start()

    # Start bot
    logger.info("Bot started!")
    application.run_polling()


if __name__ == '__main__':
    main()
