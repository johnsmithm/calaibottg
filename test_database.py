import unittest
import os
import tempfile
from datetime import datetime, timedelta
from database import Database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Create a temporary test database"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db = Database(self.db_path)

    def tearDown(self):
        """Clean up test database"""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_create_user(self):
        """Test user creation"""
        self.db.create_user(
            user_id=12345,
            username='testuser',
            name='Test User',
            height=175,
            weight=70,
            goal='lose_weight',
            goal_speed='moderate',
            daily_calorie_target=2000
        )

        user = self.db.get_user(12345)
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'testuser')
        self.assertEqual(user['name'], 'Test User')
        self.assertEqual(user['height'], 175)
        self.assertEqual(user['weight'], 70)
        self.assertEqual(user['goal'], 'lose_weight')
        self.assertEqual(user['daily_calorie_target'], 2000)

    def test_approve_user(self):
        """Test user approval"""
        self.db.create_user(
            user_id=12345,
            username='testuser',
            name='Test User',
            height=175,
            weight=70,
            goal='lose_weight',
            goal_speed='moderate',
            daily_calorie_target=2000
        )

        # User should not be approved initially
        user = self.db.get_user(12345)
        self.assertEqual(user['is_approved'], 0)

        # Approve user
        self.db.approve_user(12345)

        # User should now be approved
        user = self.db.get_user(12345)
        self.assertEqual(user['is_approved'], 1)

    def test_get_user_by_username(self):
        """Test getting user by username"""
        self.db.create_user(
            user_id=12345,
            username='testuser',
            name='Test User',
            height=175,
            weight=70,
            goal='lose_weight',
            goal_speed='moderate',
            daily_calorie_target=2000
        )

        user = self.db.get_user_by_username('testuser')
        self.assertIsNotNone(user)
        self.assertEqual(user['user_id'], 12345)
        self.assertEqual(user['name'], 'Test User')

        # Test non-existent user
        user = self.db.get_user_by_username('nonexistent')
        self.assertIsNone(user)

    def test_update_user(self):
        """Test user update"""
        self.db.create_user(
            user_id=12345,
            username='testuser',
            name='Test User',
            height=175,
            weight=70,
            goal='lose_weight',
            goal_speed='moderate',
            daily_calorie_target=2000
        )

        # Update weight
        self.db.update_user(12345, weight=75)

        user = self.db.get_user(12345)
        self.assertEqual(user['weight'], 75)

    def test_meal_times(self):
        """Test meal time settings"""
        self.db.create_user(
            user_id=12345,
            username='testuser',
            name='Test User',
            height=175,
            weight=70,
            goal='lose_weight',
            goal_speed='moderate',
            daily_calorie_target=2000
        )

        # Set meal times
        self.db.set_meal_time(12345, 'breakfast', '08:00')
        self.db.set_meal_time(12345, 'lunch', '13:00')
        self.db.set_meal_time(12345, 'dinner', '19:00')

        meal_times = self.db.get_meal_times(12345)
        self.assertEqual(meal_times['breakfast'], '08:00')
        self.assertEqual(meal_times['lunch'], '13:00')
        self.assertEqual(meal_times['dinner'], '19:00')

    def test_pending_meals(self):
        """Test pending meal operations"""
        self.db.create_user(
            user_id=12345,
            username='testuser',
            name='Test User',
            height=175,
            weight=70,
            goal='lose_weight',
            goal_speed='moderate',
            daily_calorie_target=2000
        )

        meal_data = {
            'meal_type': 'lunch',
            'calories': 500,
            'protein': 30,
            'carbs': 60,
            'fat': 15,
            'fiber': 10,
            'sugar': 5,
            'description': 'Chicken salad'
        }

        # Save pending meal
        self.db.save_pending_meal(12345, meal_data)

        # Retrieve pending meal
        pending = self.db.get_pending_meal(12345)
        self.assertIsNotNone(pending)
        self.assertEqual(pending['description'], 'Chicken salad')
        self.assertEqual(pending['calories'], 500)

        # Delete pending meal
        self.db.delete_pending_meal(12345)

        pending = self.db.get_pending_meal(12345)
        self.assertIsNone(pending)

    def test_save_meal(self):
        """Test saving meals"""
        self.db.create_user(
            user_id=12345,
            username='testuser',
            name='Test User',
            height=175,
            weight=70,
            goal='lose_weight',
            goal_speed='moderate',
            daily_calorie_target=2000
        )

        meal_data = {
            'meal_type': 'lunch',
            'calories': 500,
            'protein': 30,
            'carbs': 60,
            'fat': 15,
            'fiber': 10,
            'sugar': 5,
            'description': 'Chicken salad',
            'image_path': '/path/to/image.jpg'
        }

        self.db.save_meal(12345, meal_data)

        # Get meals
        now = datetime.now()
        start = now - timedelta(days=1)
        end = now + timedelta(days=1)

        meals = self.db.get_meals_by_date_range(12345, start, end)
        self.assertEqual(len(meals), 1)
        self.assertEqual(meals[0]['description'], 'Chicken salad')
        self.assertEqual(meals[0]['calories'], 500)

    def test_get_stats(self):
        """Test getting statistics"""
        self.db.create_user(
            user_id=12345,
            username='testuser',
            name='Test User',
            height=175,
            weight=70,
            goal='lose_weight',
            goal_speed='moderate',
            daily_calorie_target=2000
        )

        # Add multiple meals
        meal1 = {
            'meal_type': 'breakfast',
            'calories': 400,
            'protein': 20,
            'carbs': 50,
            'fat': 10,
            'fiber': 5,
            'sugar': 10,
            'description': 'Oatmeal with fruits'
        }

        meal2 = {
            'meal_type': 'lunch',
            'calories': 600,
            'protein': 40,
            'carbs': 70,
            'fat': 20,
            'fiber': 8,
            'sugar': 5,
            'description': 'Grilled chicken with rice'
        }

        self.db.save_meal(12345, meal1)
        self.db.save_meal(12345, meal2)

        # Get stats
        now = datetime.now()
        start = now - timedelta(days=1)
        end = now + timedelta(days=1)

        stats = self.db.get_stats(12345, start, end)

        self.assertEqual(stats['meal_count'], 2)
        self.assertEqual(stats['total_calories'], 1000)
        self.assertEqual(stats['total_protein'], 60)
        self.assertEqual(stats['total_carbs'], 120)
        self.assertEqual(stats['total_fat'], 30)
        self.assertEqual(stats['total_fiber'], 13)
        self.assertEqual(stats['total_sugar'], 15)
        self.assertEqual(stats['avg_calories'], 500)

    def test_get_all_users(self):
        """Test getting all users"""
        # Create multiple users
        self.db.create_user(
            user_id=11111,
            username='user1',
            name='User One',
            height=170,
            weight=65,
            goal='maintain',
            goal_speed='moderate',
            daily_calorie_target=2000
        )

        self.db.create_user(
            user_id=22222,
            username='user2',
            name='User Two',
            height=180,
            weight=80,
            goal='lose_weight',
            goal_speed='fast',
            daily_calorie_target=1800
        )

        users = self.db.get_all_users()
        self.assertEqual(len(users), 2)

        usernames = [u['username'] for u in users]
        self.assertIn('user1', usernames)
        self.assertIn('user2', usernames)

    def test_onboarding_progress_persists_partial_answers(self):
        """Test partial onboarding data is stored before profile completion"""
        self.db.save_onboarding_progress(33333, username='partialuser', name='Partial User')
        self.db.save_onboarding_progress(33333, height=172, weight=68)

        progress = self.db.get_onboarding_progress(33333)
        self.assertIsNotNone(progress)
        self.assertEqual(progress['username'], 'partialuser')
        self.assertEqual(progress['name'], 'Partial User')
        self.assertEqual(progress['height'], 172)
        self.assertEqual(progress['weight'], 68)
        self.assertIsNone(progress['goal'])

    def test_get_all_users_includes_partial_onboarding_records(self):
        """Test admin views include users who only partially completed onboarding"""
        self.db.save_onboarding_progress(44444, username='pendinguser', name='Pending User')

        users = self.db.get_all_users()
        partial_user = next((u for u in users if u['user_id'] == 44444), None)

        self.assertIsNotNone(partial_user)
        self.assertEqual(partial_user['username'], 'pendinguser')
        self.assertEqual(partial_user['name'], 'Pending User')
        self.assertEqual(partial_user['is_approved'], 0)
        self.assertIsNone(partial_user['daily_calorie_target'])


if __name__ == '__main__':
    unittest.main()
