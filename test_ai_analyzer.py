import unittest
import os
import json
from unittest.mock import Mock, patch, MagicMock
from ai_analyzer import AIAnalyzer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TestAIAnalyzer(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures"""
        # Use environment API key for tests
        self.api_key = os.getenv('GOOGLE_AI_API_KEY')
        if not self.api_key:
            self.skipTest("GOOGLE_AI_API_KEY not found in environment")

        self.analyzer = AIAnalyzer(api_key=self.api_key)

    def test_analyzer_initialization_with_key(self):
        """Test that analyzer initializes with custom API key"""
        custom_analyzer = AIAnalyzer(api_key='test_key_123')
        self.assertIsNotNone(custom_analyzer)
        self.assertIsNotNone(custom_analyzer.model)

    def test_analyzer_initialization_without_key(self):
        """Test that analyzer initializes with environment key"""
        analyzer = AIAnalyzer()
        self.assertIsNotNone(analyzer)
        self.assertIsNotNone(analyzer.model)

    @patch('ai_analyzer.genai.GenerativeModel')
    def test_analyze_food_image_structure(self, mock_model):
        """Test that analyze_food_image returns correct structure"""
        # Mock the response
        mock_response = Mock()
        mock_response.text = json.dumps({
            "description": "Grilled chicken with vegetables",
            "calories": 450,
            "protein": 35,
            "carbs": 30,
            "fat": 20,
            "fiber": 8,
            "sugar": 5,
            "meal_type": "lunch",
            "ingredients": [
                {"name": "Chicken breast", "amount": "150g", "calories": 250},
                {"name": "Broccoli", "amount": "100g", "calories": 50}
            ]
        })

        mock_model_instance = Mock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance

        analyzer = AIAnalyzer()

        # Create a dummy image path (won't actually be read due to mocking)
        result = analyzer.analyze_food_image('/tmp/test.jpg')

        # Verify structure
        self.assertIn('description', result)
        self.assertIn('calories', result)
        self.assertIn('protein', result)
        self.assertIn('carbs', result)
        self.assertIn('fat', result)
        self.assertIn('fiber', result)
        self.assertIn('sugar', result)
        self.assertIn('meal_type', result)
        self.assertIn('ingredients', result)

        # Verify data types
        self.assertIsInstance(result['description'], str)
        self.assertIsInstance(result['calories'], (int, float))
        self.assertIsInstance(result['protein'], (int, float))
        self.assertIsInstance(result['ingredients'], list)

    @patch('ai_analyzer.genai.GenerativeModel')
    def test_analyze_text_meal_structure(self, mock_model):
        """Test that analyze_text_meal returns correct structure"""
        # Mock the response
        mock_response = Mock()
        mock_response.text = json.dumps({
            "description": "Pizza margherita",
            "calories": 800,
            "protein": 30,
            "carbs": 90,
            "fat": 35,
            "fiber": 5,
            "sugar": 8,
            "meal_type": "dinner"
        })

        mock_model_instance = Mock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance

        analyzer = AIAnalyzer()

        result = analyzer.analyze_text_meal("I ate a large pizza")

        # Verify structure
        self.assertIn('description', result)
        self.assertIn('calories', result)
        self.assertIn('protein', result)
        self.assertIn('carbs', result)
        self.assertIn('fat', result)
        self.assertIn('fiber', result)
        self.assertIn('sugar', result)
        self.assertIn('meal_type', result)

        # Verify data types
        self.assertIsInstance(result['description'], str)
        self.assertIsInstance(result['calories'], (int, float))

    @patch('ai_analyzer.genai.GenerativeModel')
    def test_parse_user_intent_get_stats(self, mock_model):
        """Test parsing user intent for getting stats"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "action": "get_stats",
            "period": "week",
            "field": None,
            "value": None,
            "confidence": 0.95
        })

        mock_model_instance = Mock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance

        analyzer = AIAnalyzer()
        user_data = {'name': 'Test', 'weight': 70, 'height': 175, 'goal': 'maintain', 'goal_speed': 'moderate'}

        result = analyzer.parse_user_intent("show me my stats for this week", user_data)

        self.assertEqual(result['action'], 'get_stats')
        self.assertEqual(result['period'], 'week')

    @patch('ai_analyzer.genai.GenerativeModel')
    def test_parse_user_intent_update_setting(self, mock_model):
        """Test parsing user intent for updating settings"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "action": "update_setting",
            "period": None,
            "field": "weight",
            "value": 75,
            "confidence": 0.9
        })

        mock_model_instance = Mock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance

        analyzer = AIAnalyzer()
        user_data = {'name': 'Test', 'weight': 70, 'height': 175, 'goal': 'maintain', 'goal_speed': 'moderate'}

        result = analyzer.parse_user_intent("change my weight to 75kg", user_data)

        self.assertEqual(result['action'], 'update_setting')
        self.assertEqual(result['field'], 'weight')
        self.assertEqual(result['value'], 75)

    @patch('ai_analyzer.genai.GenerativeModel')
    def test_parse_natural_command(self, mock_model):
        """Test parsing natural language commands"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "action": "update_meal_time",
            "field": "breakfast_time",
            "value": "08:00",
            "confidence": 0.88
        })

        mock_model_instance = Mock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance

        analyzer = AIAnalyzer()
        user_data = {'name': 'Test', 'weight': 70, 'height': 175, 'goal': 'maintain', 'goal_speed': 'moderate'}

        result = analyzer.parse_natural_command("set breakfast reminder to 8am", user_data)

        self.assertEqual(result['action'], 'update_meal_time')
        self.assertEqual(result['field'], 'breakfast_time')
        self.assertEqual(result['value'], '08:00')

    @patch('ai_analyzer.genai.GenerativeModel')
    def test_json_parsing_with_markdown_code_blocks(self, mock_model):
        """Test that JSON extraction works with markdown code blocks"""
        mock_response = Mock()
        mock_response.text = """```json
{
    "description": "Salad",
    "calories": 300,
    "protein": 15,
    "carbs": 25,
    "fat": 15,
    "fiber": 10,
    "sugar": 5,
    "meal_type": "lunch"
}
```"""

        mock_model_instance = Mock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance

        analyzer = AIAnalyzer()

        result = analyzer.analyze_text_meal("I ate a salad")

        # Should successfully extract JSON from markdown
        self.assertEqual(result['description'], 'Salad')
        self.assertEqual(result['calories'], 300)

    @patch('ai_analyzer.genai.GenerativeModel')
    def test_json_parsing_without_code_blocks(self, mock_model):
        """Test that JSON extraction works without markdown code blocks"""
        mock_response = Mock()
        mock_response.text = """{
    "description": "Burger",
    "calories": 700,
    "protein": 30,
    "carbs": 50,
    "fat": 40,
    "fiber": 3,
    "sugar": 10,
    "meal_type": "dinner"
}"""

        mock_model_instance = Mock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance

        analyzer = AIAnalyzer()

        result = analyzer.analyze_text_meal("I ate a burger")

        # Should successfully extract plain JSON
        self.assertEqual(result['description'], 'Burger')
        self.assertEqual(result['calories'], 700)


if __name__ == '__main__':
    unittest.main()
