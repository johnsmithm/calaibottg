# Calorie Tracker Bot - Recent Changes

This document summarizes all the new features and improvements added to the bot.

## 🎉 New Features

### 1. **Admin Approval System**
- New `is_approved` field in users table
- Users must be approved by admin or provide their own Gemini API key
- Prevents unauthorized usage and controls API costs

**Admin Commands:**
- `/approve @username` - Approve a user to use the bot
- `/seealluserstats` - View statistics for all users

**Files Modified:**
- `database.py` - Added `approve_user()`, `get_user_by_username()`, `get_all_users()`
- `bot.py` - Added approval checks in photo/voice/text handlers
- `.env` - Added `ADMIN_USER_ID` variable

### 2. **User API Key Support**
- Users can provide their own Gemini API key
- Approved users can use shared admin API key
- Flexible access control

**Database Changes:**
- New `gemini_api_key` field in users table
- New `username` field to identify users

**Files Modified:**
- `database.py` - Updated schema
- `ai_analyzer.py` - Support for custom API keys
- `bot.py` - Use user's API key when available

### 3. **Moldova Timezone Support**
- Reminders now use Europe/Chisinau timezone
- Accurate meal time notifications

**Files Modified:**
- `reminder_scheduler.py` - Added pytz timezone support
- `.env` - Added `TIMEZONE` variable
- `requirements.txt` - Added pytz==2024.1

### 4. **Enhanced Stats Display After Meal Save**
- Beautiful progress bar showing daily progress
- Detailed macro breakdown (protein, carbs, fat)
- Total meals count for the day
- Remaining calories display

**Example Output:**
```
✅ Meal Saved!

📊 TODAY'S PROGRESS
████████████░░░░░░░░ 60.5%

⚡️ 1210 / 2000 kcal
📊 Remaining: 790 kcal

MACROS TODAY:
🥩 Protein: 85g
🍞 Carbs: 120g
🥑 Fat: 45g

🍽 Meals today: 3
```

**Files Modified:**
- `bot.py` - Updated `button_callback()` save_meal section

### 5. **Ingredient Breakdown Prediction**
- AI now predicts individual ingredients with portions
- Shows calories per ingredient
- More detailed nutritional tracking

**Example Output:**
```
📊 Nutritional Information:

🍽 Chicken salad with vegetables
🍴 Meal Type: Lunch

INGREDIENTS:
• Chicken breast (150g) - 250 kcal
• Mixed greens (100g) - 50 kcal
• Cherry tomatoes (80g) - 20 kcal
• Olive oil (10ml) - 90 kcal

TOTAL:
⚡️ Calories: 410 kcal
🥩 Protein: 35g
🍞 Carbs: 15g
🥑 Fat: 25g
🌾 Fiber: 8g
🍬 Sugar: 5g
```

**Files Modified:**
- `ai_analyzer.py` - Updated prompt to include ingredients
- `bot.py` - Added `format_meal_message()` helper function

### 6. **/yesterday Command**
- Instagram-ready formatting
- Breakdown by meal type (breakfast, lunch, dinner, snacks)
- Beautiful summary with daily macros
- Target comparison

**Example Output:**
```
📅 March 25, 2026
==============================

📊 DAILY SUMMARY
⚡️ Total Calories: 1850 kcal
🍽 Meals Logged: 4

MACROS:
🥩 Protein: 120g
🍞 Carbs: 180g
🥑 Fat: 65g
🌾 Fiber: 30g

🌅 BREAKFAST (1 meal)
   • Oatmeal with fruits and nuts... (450 kcal)

🌞 LUNCH (1 meal)
   • Grilled chicken with quinoa... (550 kcal)

🌙 DINNER (1 meal)
   • Salmon with roasted vegetables... (650 kcal)

🍿 SNACKS (1 snack)
   • Greek yogurt with berries... (200 kcal)

==============================
🎯 Target: 2000 kcal
📉 Under by: 150 kcal
```

**Files Modified:**
- `bot.py` - Added `yesterday_command()`

### 7. **Username Tracking**
- Saves Telegram username during onboarding
- Enables admin to approve by username
- Better user identification

**Files Modified:**
- `database.py` - Added username field
- `bot.py` - Save username in `get_dinner_time()`

## 📝 Updated Commands

### New Commands
- `/yesterday` - Yesterday's stats in Instagram-ready format
- `/approve @username` - [Admin] Approve user
- `/seealluserstats` - [Admin] View all users

### Updated Help
The `/help` command now includes the new `/yesterday` command.

## 🔧 Technical Improvements

### Database Schema Updates
```sql
-- New fields in users table
ALTER TABLE users ADD COLUMN username TEXT;
ALTER TABLE users ADD COLUMN gemini_api_key TEXT;
ALTER TABLE users ADD COLUMN is_approved INTEGER DEFAULT 0;
```

### New Database Methods
- `approve_user(user_id)` - Approve a user
- `get_all_users()` - Get all users ordered by creation date
- `get_user_by_username(username)` - Find user by Telegram username

### AI Improvements
- Custom API key support in `AIAnalyzer.__init__()`
- Ingredient breakdown in image analysis
- More detailed meal descriptions

## 🧪 Testing

### New Test Files
- `test_database.py` - 9 comprehensive tests
- `test_calorie_calculator.py` - 11 tests for all scenarios
- `test_ai_analyzer.py` - 10+ tests with mocking
- `test_bot_commands.py` - 17 tests for helpers and utilities

### Test Coverage
- ✅ Database operations (CRUD, stats, approval)
- ✅ Calorie calculations (lose/gain/maintain)
- ✅ Time parsing (12hr/24hr formats)
- ✅ Message formatting with/without ingredients
- ✅ Progress bar rendering
- ✅ Date range calculations

### Test Execution
```bash
./run_tests.sh
```

**Results:** All 47+ tests passing ✅

## 📄 Documentation

### New Files
- `TESTING.md` - Comprehensive testing guide
- `CHANGES.md` - This file
- `run_tests.sh` - Automated test runner

### Updated Files
- `botfather_commands.txt` - Added new commands
- `.env` - Added ADMIN_USER_ID and TIMEZONE
- `requirements.txt` - Added pytz

## 🚀 Deployment Notes

### Environment Variables Required
```bash
TELEGRAM_BOT_TOKEN=your_token_here
GOOGLE_AI_API_KEY=your_gemini_key_here
ADMIN_USER_ID=your_telegram_user_id
TIMEZONE=Europe/Chisinau
```

### Getting Admin User ID
1. Use @userinfobot on Telegram
2. Check bot logs when you send a message
3. See TESTING.md for detailed instructions

### Railway Deployment
All changes are compatible with existing Railway deployment. Just update environment variables in Railway dashboard.

## 📊 Statistics

### Code Changes
- Files modified: 8
- New functions added: 5
- New commands: 3
- Database schema updates: 3 fields
- Tests added: 47+
- Lines of code added: ~1000+

### Features Summary
| Feature | Status | Priority |
|---------|--------|----------|
| Moldova timezone | ✅ Complete | High |
| Enhanced stats after save | ✅ Complete | High |
| Ingredient breakdown | ✅ Complete | Medium |
| Admin approval system | ✅ Complete | High |
| User API key support | ✅ Complete | High |
| /yesterday command | ✅ Complete | Medium |
| /approve command | ✅ Complete | High |
| /seealluserstats | ✅ Complete | Medium |
| Comprehensive tests | ✅ Complete | High |

## 🔜 Future Enhancements

Potential improvements for consideration:

1. **Export functionality** - Export stats to CSV/PDF
2. **Goals tracking** - Weekly/monthly goal progress
3. **Photo gallery** - View past meal photos
4. **Meal templates** - Save frequently eaten meals
5. **Barcode scanning** - Scan product barcodes
6. **Water tracking** - Log daily water intake
7. **Exercise logging** - Track workouts and calories burned
8. **Social features** - Share meals with friends
9. **Meal planning** - Plan meals for the week
10. **Notifications** - Customizable reminder messages

## 💡 Tips for Users

1. **Get Approved:** Contact @imosnoi to get approved for free access
2. **Own API Key:** Alternatively, provide your own Gemini API key
3. **Use /yesterday:** Great for sharing daily summaries on social media
4. **Natural Language:** Use natural commands like "show my stats"
5. **Progress Tracking:** Check progress bar after each meal save

## 🐛 Known Issues

None at this time. All tests passing.

## 📞 Support

For issues or questions:
- Check `TESTING.md` for testing guide
- Review `README.md` for general usage
- Contact admin @imosnoi for approval

---

**Last Updated:** March 26, 2026
**Version:** 2.0.0
**Status:** Production Ready ✅
