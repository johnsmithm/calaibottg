# Testing Guide

This document describes how to run tests for the Calorie Tracker Bot.

## Test Suite Overview

The test suite includes:

1. **Database Tests** (`test_database.py`) - 9 tests
   - User creation and retrieval
   - User approval system
   - Meal times management
   - Pending meals workflow
   - Meal storage and statistics

2. **Calorie Calculator Tests** (`test_calorie_calculator.py`) - 11 tests
   - Weight loss calculations (slow/moderate/fast)
   - Weight gain calculations (slow/moderate/fast)
   - Weight maintenance calculations
   - Edge cases and validation

3. **AI Analyzer Tests** (`test_ai_analyzer.py`) - 10+ tests
   - Food image analysis (mocked)
   - Text meal analysis (mocked)
   - User intent parsing
   - Natural language command parsing
   - JSON extraction from various formats

4. **Bot Commands Tests** (`test_bot_commands.py`) - 17 tests
   - Time parsing (12hr/24hr formats)
   - Meal message formatting
   - Ingredient display
   - Progress bar rendering
   - Date range calculations

## Prerequisites

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file with the following variables:

```bash
# Telegram Bot Token
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Google AI API Key (Gemini)
GOOGLE_AI_API_KEY=your_gemini_api_key_here

# Admin User ID
ADMIN_USER_ID=0

# Timezone
TIMEZONE=Europe/Chisinau
```

**Important:** For `ADMIN_USER_ID`, use `0` as a placeholder until you get your actual user ID (see below).

## Running Tests

### Run All Tests

```bash
./run_tests.sh
```

This will run all test suites and display a summary.

### Run Individual Test Suites

```bash
# Database tests
python3 -m unittest test_database -v

# Calorie calculator tests
python3 -m unittest test_calorie_calculator -v

# AI analyzer tests
python3 -m unittest test_ai_analyzer -v

# Bot commands tests
python3 -m unittest test_bot_commands -v
```

### Run Specific Test

```bash
# Run a specific test class
python3 -m unittest test_database.TestDatabase -v

# Run a specific test method
python3 -m unittest test_database.TestDatabase.test_create_user -v
```

## Test Results

All tests should pass:

```
================================
Test Results Summary
================================
✅ Database Tests: PASSED (9 tests)
✅ Calorie Calculator Tests: PASSED (11 tests)
✅ AI Analyzer Tests: PASSED (10+ tests)
✅ Bot Commands Tests: PASSED (17 tests)

🎉 All tests passed!
```

## Getting Your Admin User ID

To use admin commands like `/approve` and `/seealluserstats`, you need to set your Telegram user ID:

### Method 1: Use @userinfobot

1. Open Telegram
2. Search for `@userinfobot`
3. Send `/start` to the bot
4. It will reply with your user ID
5. Update `.env` file: `ADMIN_USER_ID=your_user_id_here`

### Method 2: Check Bot Logs

1. Start the bot locally: `python3 bot.py`
2. Send a message to your bot
3. Check the console logs - your user ID will appear
4. Update `.env` file with the ID

### Method 3: Add Logging Temporarily

Add this to `bot.py` in any handler:

```python
logger.info(f"User ID: {update.effective_user.id}")
logger.info(f"Username: {update.effective_user.username}")
```

## Continuous Integration

For CI/CD pipelines, ensure:

1. Environment variables are set
2. All dependencies are installed
3. Tests run with verbose output for debugging

Example GitHub Actions workflow:

```yaml
- name: Run Tests
  env:
    TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    GOOGLE_AI_API_KEY: ${{ secrets.GOOGLE_AI_API_KEY }}
    ADMIN_USER_ID: 0
    TIMEZONE: Europe/Chisinau
  run: |
    pip install -r requirements.txt
    ./run_tests.sh
```

## Test Coverage

The tests cover:

- ✅ All database operations
- ✅ Calorie calculations for all scenarios
- ✅ AI response parsing (mocked)
- ✅ Time parsing utilities
- ✅ Message formatting
- ✅ Progress bar rendering
- ✅ Date range calculations

## Known Issues

### Python Version Warnings

You may see warnings about Python 3.9 being deprecated. These are safe to ignore for testing, but consider upgrading to Python 3.10+ for production.

### API Key Tests

Some AI analyzer tests are mocked to avoid using real API calls. To test with real Gemini API:

1. Ensure `GOOGLE_AI_API_KEY` is set in `.env`
2. Remove mocking from specific tests
3. Be aware this will consume API quota

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError`, install dependencies:

```bash
pip install -r requirements.txt
```

### Database Lock Errors

Tests use temporary databases, but if you see lock errors:

```bash
# Clean up any test artifacts
rm -f test_*.db
```

### Environment Variable Errors

Make sure `.env` exists and all required variables are set:

```bash
cat .env
```

## Writing New Tests

When adding new features:

1. Create tests first (TDD approach)
2. Use descriptive test names
3. Test edge cases
4. Mock external API calls
5. Clean up resources in `tearDown()`

Example:

```python
def test_new_feature(self):
    """Test description"""
    # Setup
    expected = "result"

    # Execute
    actual = my_function()

    # Assert
    self.assertEqual(actual, expected)
```
