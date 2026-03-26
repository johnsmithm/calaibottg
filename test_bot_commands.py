import unittest
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from dotenv import load_dotenv

# Load environment before importing bot modules
load_dotenv()

# Mock all required modules before importing bot
import sys
sys.modules['telegram'] = MagicMock()
sys.modules['telegram.ext'] = MagicMock()
sys.modules['speech_recognition'] = MagicMock()
sys.modules['pydub'] = MagicMock()
sys.modules['schedule'] = MagicMock()
sys.modules['pytz'] = MagicMock()

from bot import parse_time, format_meal_message


class TestBotHelpers(unittest.TestCase):

    def test_parse_time_12hr_am(self):
        """Test parsing 12-hour AM format"""
        self.assertEqual(parse_time('8am'), '08:00')
        self.assertEqual(parse_time('8:30am'), '08:30')
        self.assertEqual(parse_time('12am'), '00:00')

    def test_parse_time_12hr_pm(self):
        """Test parsing 12-hour PM format"""
        self.assertEqual(parse_time('1pm'), '13:00')
        self.assertEqual(parse_time('2:30pm'), '14:30')
        self.assertEqual(parse_time('12pm'), '12:00')

    def test_parse_time_24hr(self):
        """Test parsing 24-hour format"""
        self.assertEqual(parse_time('08:00'), '08:00')
        self.assertEqual(parse_time('13:30'), '13:30')
        self.assertEqual(parse_time('20:45'), '20:45')

    def test_parse_time_single_digit(self):
        """Test parsing single digit hours"""
        self.assertEqual(parse_time('8'), '08:00')
        self.assertEqual(parse_time('9am'), '09:00')

    def test_format_meal_message_without_ingredients(self):
        """Test meal message formatting without ingredients"""
        meal_data = {
            'description': 'Grilled chicken with rice',
            'meal_type': 'lunch',
            'calories': 500,
            'protein': 40,
            'carbs': 60,
            'fat': 15,
            'fiber': 8,
            'sugar': 5
        }

        message = format_meal_message(meal_data)

        self.assertIn('Grilled chicken with rice', message)
        self.assertIn('Lunch', message)
        self.assertIn('500 kcal', message)
        self.assertIn('40g', message)  # protein
        self.assertIn('Save this meal?', message)

    def test_format_meal_message_with_ingredients(self):
        """Test meal message formatting with ingredients"""
        meal_data = {
            'description': 'Chicken salad',
            'meal_type': 'lunch',
            'calories': 400,
            'protein': 35,
            'carbs': 30,
            'fat': 15,
            'fiber': 10,
            'sugar': 5,
            'ingredients': [
                {'name': 'Chicken breast', 'amount': '150g', 'calories': 250},
                {'name': 'Mixed greens', 'amount': '100g', 'calories': 50},
                {'name': 'Olive oil', 'amount': '10ml', 'calories': 90}
            ]
        }

        message = format_meal_message(meal_data)

        self.assertIn('INGREDIENTS:', message)
        self.assertIn('Chicken breast', message)
        self.assertIn('150g', message)
        self.assertIn('250 kcal', message)
        self.assertIn('Mixed greens', message)
        self.assertIn('Olive oil', message)
        self.assertIn('TOTAL:', message)
        self.assertIn('400 kcal', message)


class TestBotCommandsIntegration(unittest.TestCase):
    """Integration tests for bot command structure"""

    def test_meal_type_classification(self):
        """Test that meal types are properly handled"""
        valid_meal_types = ['breakfast', 'lunch', 'dinner', 'snack']

        for meal_type in valid_meal_types:
            meal_data = {
                'description': f'Test {meal_type}',
                'meal_type': meal_type,
                'calories': 300,
                'protein': 20,
                'carbs': 30,
                'fat': 10,
                'fiber': 5,
                'sugar': 3
            }

            message = format_meal_message(meal_data)
            self.assertIn(meal_type.title(), message)

    def test_calorie_formatting(self):
        """Test that calories are formatted correctly"""
        meal_data = {
            'description': 'Test meal',
            'meal_type': 'lunch',
            'calories': 525.7,
            'protein': 30,
            'carbs': 40,
            'fat': 20,
            'fiber': 8,
            'sugar': 5
        }

        message = format_meal_message(meal_data)

        # Should display as integer in message
        self.assertIn('525', message)

    def test_ingredient_display_format(self):
        """Test ingredient display formatting"""
        meal_data = {
            'description': 'Pasta',
            'meal_type': 'dinner',
            'calories': 600,
            'protein': 25,
            'carbs': 80,
            'fat': 20,
            'fiber': 6,
            'sugar': 8,
            'ingredients': [
                {'name': 'Spaghetti', 'amount': '200g', 'calories': 350},
                {'name': 'Tomato sauce', 'amount': '100g', 'calories': 150},
                {'name': 'Parmesan', 'amount': '30g', 'calories': 100}
            ]
        }

        message = format_meal_message(meal_data)

        # Check each ingredient is formatted correctly
        self.assertIn('• Spaghetti (200g) - 350 kcal', message)
        self.assertIn('• Tomato sauce (100g) - 150 kcal', message)
        self.assertIn('• Parmesan (30g) - 100 kcal', message)

    def test_empty_ingredients_list(self):
        """Test handling of empty ingredients list"""
        meal_data = {
            'description': 'Simple meal',
            'meal_type': 'snack',
            'calories': 200,
            'protein': 10,
            'carbs': 25,
            'fat': 8,
            'fiber': 3,
            'sugar': 5,
            'ingredients': []
        }

        message = format_meal_message(meal_data)

        # Should not show INGREDIENTS section if empty
        self.assertNotIn('INGREDIENTS:', message)
        self.assertIn('200 kcal', message)


class TestProgressBarCalculation(unittest.TestCase):
    """Test progress bar calculation logic"""

    def test_progress_percentage_calculation(self):
        """Test percentage calculation for progress bars"""
        target = 2000
        consumed = 1500

        percentage = (consumed / target * 100) if target > 0 else 0

        self.assertAlmostEqual(percentage, 75.0, places=1)

    def test_progress_bar_rendering(self):
        """Test progress bar rendering logic"""
        bar_length = 20

        # Test 50% progress
        percentage = 50
        filled = int(bar_length * percentage / 100)
        bar = "█" * filled + "░" * (bar_length - filled)

        self.assertEqual(len(bar), 20)
        self.assertEqual(filled, 10)
        self.assertIn('█', bar)
        self.assertIn('░', bar)

    def test_progress_bar_edge_cases(self):
        """Test progress bar at 0% and 100%"""
        bar_length = 20

        # 0% progress
        percentage = 0
        filled = int(bar_length * percentage / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        self.assertEqual(bar, "░" * 20)

        # 100% progress
        percentage = 100
        filled = int(bar_length * percentage / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        self.assertEqual(bar, "█" * 20)

        # Over 100% progress
        percentage = 125
        filled = int(bar_length * percentage / 100)
        bar = "█" * min(filled, bar_length) + "░" * max(0, bar_length - filled)
        self.assertEqual(len(bar), 20)


class TestDateRangeCalculations(unittest.TestCase):
    """Test date range calculations for statistics"""

    def test_today_date_range(self):
        """Test today's date range calculation"""
        now = datetime.now()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        self.assertEqual(start.hour, 0)
        self.assertEqual(start.minute, 0)
        self.assertEqual((end - start).days, 1)

    def test_yesterday_date_range(self):
        """Test yesterday's date range calculation"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today - timedelta(days=1)
        yesterday_end = today

        self.assertEqual((yesterday_end - yesterday_start).days, 1)
        self.assertLess(yesterday_start, today)

    def test_week_date_range(self):
        """Test week date range calculation"""
        now = datetime.now()
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)

        self.assertEqual(start.weekday(), 0)  # Monday
        self.assertEqual((end - start).days, 7)

    def test_month_date_range(self):
        """Test month date range calculation"""
        now = datetime.now()
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if now.month == 12:
            end = start.replace(year=now.year+1, month=1)
        else:
            end = start.replace(month=now.month+1)

        self.assertEqual(start.day, 1)
        self.assertGreater(end, start)


if __name__ == '__main__':
    unittest.main()
