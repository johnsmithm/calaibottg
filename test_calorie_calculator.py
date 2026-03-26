import unittest
from calorie_calculator import calculate_daily_calorie_target


class TestCalorieCalculator(unittest.TestCase):

    def test_lose_weight_slow(self):
        """Test calorie calculation for slow weight loss"""
        target = calculate_daily_calorie_target(
            weight=80,
            height=180,
            goal='lose_weight',
            goal_speed='slow'
        )
        # Should be TDEE - 250 kcal (0.25 kg/week deficit)
        # Approximate TDEE for 80kg, 180cm: ~2400 kcal
        self.assertIsInstance(target, (int, float))
        self.assertGreater(target, 1500)
        self.assertLess(target, 3000)

    def test_lose_weight_moderate(self):
        """Test calorie calculation for moderate weight loss"""
        target = calculate_daily_calorie_target(
            weight=80,
            height=180,
            goal='lose_weight',
            goal_speed='moderate'
        )
        # Should be TDEE - 500 kcal (0.5 kg/week deficit)
        self.assertIsInstance(target, (int, float))
        self.assertGreater(target, 1400)
        self.assertLess(target, 2500)

    def test_lose_weight_fast(self):
        """Test calorie calculation for fast weight loss"""
        target = calculate_daily_calorie_target(
            weight=80,
            height=180,
            goal='lose_weight',
            goal_speed='fast'
        )
        # Should be TDEE - 750 kcal (0.75 kg/week deficit)
        self.assertIsInstance(target, (int, float))
        self.assertGreater(target, 1200)
        self.assertLess(target, 2200)

    def test_gain_weight_slow(self):
        """Test calorie calculation for slow weight gain"""
        target = calculate_daily_calorie_target(
            weight=70,
            height=175,
            goal='gain_weight',
            goal_speed='slow'
        )
        # Should be TDEE + 250 kcal (0.25 kg/week surplus)
        self.assertIsInstance(target, (int, float))
        self.assertGreater(target, 2000)
        self.assertLess(target, 3500)

    def test_gain_weight_moderate(self):
        """Test calorie calculation for moderate weight gain"""
        target = calculate_daily_calorie_target(
            weight=70,
            height=175,
            goal='gain_weight',
            goal_speed='moderate'
        )
        # Should be TDEE + 500 kcal (0.5 kg/week surplus)
        self.assertIsInstance(target, (int, float))
        self.assertGreater(target, 2200)
        self.assertLess(target, 3700)

    def test_gain_weight_fast(self):
        """Test calorie calculation for fast weight gain"""
        target = calculate_daily_calorie_target(
            weight=70,
            height=175,
            goal='gain_weight',
            goal_speed='fast'
        )
        # Should be TDEE + 750 kcal (0.75 kg/week surplus)
        self.assertIsInstance(target, (int, float))
        self.assertGreater(target, 2400)
        self.assertLess(target, 3900)

    def test_maintain_weight(self):
        """Test calorie calculation for maintaining weight"""
        target = calculate_daily_calorie_target(
            weight=75,
            height=178,
            goal='maintain',
            goal_speed='moderate'  # Speed doesn't matter for maintain
        )
        # Should be TDEE without adjustment
        self.assertIsInstance(target, (int, float))
        self.assertGreater(target, 1800)
        self.assertLess(target, 3000)

    def test_different_weights(self):
        """Test that different weights produce different results"""
        target1 = calculate_daily_calorie_target(
            weight=60,
            height=170,
            goal='maintain',
            goal_speed='moderate'
        )

        target2 = calculate_daily_calorie_target(
            weight=90,
            height=170,
            goal='maintain',
            goal_speed='moderate'
        )

        # Higher weight should need more calories
        self.assertGreater(target2, target1)

    def test_different_heights(self):
        """Test that different heights produce different results"""
        target1 = calculate_daily_calorie_target(
            weight=70,
            height=160,
            goal='maintain',
            goal_speed='moderate'
        )

        target2 = calculate_daily_calorie_target(
            weight=70,
            height=190,
            goal='maintain',
            goal_speed='moderate'
        )

        # Taller person should need more calories
        self.assertGreater(target2, target1)

    def test_speed_impact_on_deficit(self):
        """Test that different speeds create appropriate calorie differences"""
        slow = calculate_daily_calorie_target(
            weight=75,
            height=175,
            goal='lose_weight',
            goal_speed='slow'
        )

        moderate = calculate_daily_calorie_target(
            weight=75,
            height=175,
            goal='lose_weight',
            goal_speed='moderate'
        )

        fast = calculate_daily_calorie_target(
            weight=75,
            height=175,
            goal='lose_weight',
            goal_speed='fast'
        )

        # Faster weight loss should have lower calorie targets
        self.assertGreater(slow, moderate)
        self.assertGreater(moderate, fast)

        # Differences should be approximately 250 kcal between levels
        self.assertAlmostEqual(slow - moderate, 250, delta=50)
        self.assertAlmostEqual(moderate - fast, 250, delta=50)

    def test_minimum_calorie_floor(self):
        """Test that extremely low weights don't produce dangerously low calorie targets"""
        target = calculate_daily_calorie_target(
            weight=40,
            height=150,
            goal='lose_weight',
            goal_speed='fast'
        )

        # Should have some minimum reasonable calorie target
        self.assertGreater(target, 1000)


if __name__ == '__main__':
    unittest.main()
