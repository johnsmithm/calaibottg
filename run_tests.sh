#!/bin/bash

# Run all unit tests for the Calorie Tracker Bot
# Uses environment variables from .env file

echo "================================"
echo "Calorie Tracker Bot - Test Suite"
echo "================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found. Some tests may fail."
    echo ""
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

echo "Running Database Tests..."
python3 -m unittest test_database -v
DB_RESULT=$?
echo ""

echo "Running Calorie Calculator Tests..."
python3 -m unittest test_calorie_calculator -v
CALC_RESULT=$?
echo ""

echo "Running AI Analyzer Tests..."
python3 -m unittest test_ai_analyzer -v
AI_RESULT=$?
echo ""

echo "Running Bot Commands Tests..."
python3 -m unittest test_bot_commands -v
BOT_RESULT=$?
echo ""

echo "================================"
echo "Test Results Summary"
echo "================================"

if [ $DB_RESULT -eq 0 ]; then
    echo "✅ Database Tests: PASSED"
else
    echo "❌ Database Tests: FAILED"
fi

if [ $CALC_RESULT -eq 0 ]; then
    echo "✅ Calorie Calculator Tests: PASSED"
else
    echo "❌ Calorie Calculator Tests: FAILED"
fi

if [ $AI_RESULT -eq 0 ]; then
    echo "✅ AI Analyzer Tests: PASSED"
else
    echo "❌ AI Analyzer Tests: FAILED"
fi

if [ $BOT_RESULT -eq 0 ]; then
    echo "✅ Bot Commands Tests: PASSED"
else
    echo "❌ Bot Commands Tests: FAILED"
fi

echo ""

# Calculate total result
TOTAL_RESULT=$(($DB_RESULT + $CALC_RESULT + $AI_RESULT + $BOT_RESULT))

if [ $TOTAL_RESULT -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "⚠️  Some tests failed. Please review the output above."
    exit 1
fi
