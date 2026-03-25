# 🍽 AI Calorie Tracker Telegram Bot

AI-powered Telegram bot for tracking calories, macros, and achieving weight goals using Gemini AI.

## ✨ Features

- 📸 **Image Analysis** - Upload meal photos for instant nutritional breakdown
- 🎤 **Voice Support** - Describe meals via voice messages
- 💬 **Text Input** - Type meal descriptions naturally
- 🎯 **Personalized Goals** - Custom calorie targets based on weight goals
- ⏰ **Smart Reminders** - Automatic meal time notifications
- 📊 **Statistics** - Track daily, weekly, monthly, and yearly progress
- 🤖 **Natural Language** - Update settings by just typing naturally
- 💾 **Persistent Storage** - SQLite database for all your data
- ✅ **Save/Cancel Flow** - Review meals before logging

## 📊 Tracked Nutrients

- Calories (kcal)
- Protein (g)
- Carbohydrates (g)
- Fat (g)
- Fiber (g)
- Sugar (g)

## 🚀 Setup

### Prerequisites

- Python 3.8 or higher
- Telegram account
- Google AI Studio API key

### Installation

1. **Clone or navigate to the project directory:**
```bash
cd /Users/ion/apps/calaitgbot
```

2. **Create virtual environment:**
```bash
python3 -m venv venv
```

3. **Activate virtual environment:**
```bash
source venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Configure environment variables:**

The `.env` file is already configured with your API keys.

### Getting API Keys

#### Telegram Bot Token
1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions
3. Copy the bot token provided

#### Google AI Studio API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

## 🎮 Usage

### Start the Bot

**Option 1: Using the start script**
```bash
./start.sh
```

**Option 2: Manual start**
```bash
source venv/bin/activate
python bot.py
```

### Bot Commands

- `/start` - Begin onboarding or restart
- `/stats` - View today's statistics
- `/stats week` - View this week's statistics
- `/stats month` - View this month's statistics
- `/stats year` - View this year's statistics
- `/help` - Show help message
- `/cancel` - Cancel current operation

### Onboarding Flow

When you first start the bot, you'll be asked:

1. **Name** - Your first name
2. **Height** - In centimeters (e.g., 175)
3. **Weight** - In kilograms (e.g., 70)
4. **Goal** - Lose weight / Gain weight / Maintain weight
5. **Goal Speed** - Slow (0.25kg/week) / Moderate (0.5kg/week) / Fast (0.75kg/week)
6. **Meal Times** - Breakfast, lunch, and dinner times for reminders

### Logging Meals

**Photo:**
- Send a photo of your meal
- AI analyzes and provides nutritional info
- Click ✅ Save or ❌ Cancel

**Voice:**
- Send a voice message describing your meal
- Speech is transcribed and analyzed
- Review and save/cancel

**Text:**
- Type a description of your meal
- AI estimates nutritional values
- Review and save/cancel

### Natural Language Commands

Update your settings by typing naturally:

```
Change my weight to 75kg
I'm 180cm tall now
Set breakfast reminder to 8am
Update lunch time to 1pm
Move dinner to 7:30pm
```

### Example Workflow

1. **Morning Reminder:** Bot sends "🌅 Good morning! Time for breakfast."
2. **Log Meal:** Send a photo of your breakfast
3. **Review:** Check AI-generated nutritional info
4. **Save:** Click ✅ Save button
5. **Progress:** See your daily calorie progress
6. **Repeat:** For lunch and dinner

## 📁 Project Structure

```
calaitgbot/
├── bot.py                    # Main bot application
├── database.py              # SQLite database operations
├── ai_analyzer.py           # Gemini AI integration
├── calorie_calculator.py    # Calorie/macro calculations
├── reminder_scheduler.py    # Meal reminder system
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not in git)
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔧 How It Works

### Calorie Calculation

The bot uses the **Mifflin-St Jeor Equation** to calculate your Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE):

**BMR Formula:**
- Male: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age + 5
- Female: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age - 161

**Activity Level:** Assumes moderate activity (1.55x multiplier)

**Calorie Adjustment:**
- Slow: ±275 kcal/day (~0.25kg/week)
- Moderate: ±550 kcal/day (~0.5kg/week)
- Fast: ±825 kcal/day (~0.75kg/week)

### AI Analysis

**Image Analysis:**
- Uses Google's Gemini 1.5 Flash model
- Analyzes food images to identify items
- Estimates portion sizes
- Calculates nutritional values

**Voice Processing:**
- Converts voice to text using Google Speech Recognition
- Analyzes text description with Gemini
- Estimates nutritional content

**Natural Language Processing:**
- Parses commands like "change weight to 75kg"
- Extracts intent and values
- Updates database automatically

### Reminders

- Runs background scheduler checking every minute
- Sends reminders at your configured meal times
- Encourages consistent meal logging

## 🛠 Troubleshooting

**Bot doesn't respond:**
- Check your Telegram Bot Token in `.env`
- Ensure the bot is running (`python bot.py`)

**AI analysis fails:**
- Verify Google AI API key in `.env`
- Check API quota limits
- Try a clearer photo or description

**Voice messages don't work:**
- Ensure internet connection (for Google Speech Recognition)
- Speak clearly when recording
- Keep messages under 1 minute

**Reminders not working:**
- Ensure bot is running continuously
- Check meal times are set correctly
- Times should be in HH:MM format

## 📝 Database Schema

**users** - User profiles and goals
**meals** - Logged meal entries
**meal_times** - Reminder time preferences
**pending_meals** - Temporary storage for save/cancel flow

## 🔐 Privacy & Security

- All data stored locally in SQLite database
- No data shared with third parties except:
  - Images sent to Google Gemini for analysis
  - Voice sent to Google for transcription
- Telegram communication is encrypted
- Database file: `calorie_tracker.db`

## 🎯 Tips for Best Results

1. **Clear Photos** - Take well-lit, clear photos of meals
2. **Complete Plates** - Show entire meal in frame
3. **Detailed Voice** - Mention portions (e.g., "200g chicken breast")
4. **Consistent Logging** - Track all meals for accurate stats
5. **Regular Weigh-ins** - Update weight weekly for better targets
6. **Honest Tracking** - Include snacks and drinks

## 🚧 Known Limitations

- AI estimates may not be 100% accurate
- Requires active internet connection
- Voice recognition works best in quiet environments
- Complex meals may need manual adjustments

## 📈 Future Enhancements

- [ ] Barcode scanning
- [ ] Custom food database
- [ ] Meal planning suggestions
- [ ] Integration with fitness trackers
- [ ] Export data to CSV
- [ ] Multi-language support
- [ ] Recipe suggestions based on targets

## 📄 License

MIT License - Feel free to use and modify

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📞 Support

For issues or questions, please check:
1. This README
2. `/help` command in bot
3. Logs in terminal

---

**Built with ❤️ using Python, Telegram Bot API, and Google Gemini AI**
