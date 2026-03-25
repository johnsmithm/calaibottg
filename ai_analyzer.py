import google.generativeai as genai
import os
from PIL import Image
import json

class AIAnalyzer:
    def __init__(self):
        genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def analyze_food_image(self, image_path):
        """Analyze food image and extract nutritional information using Gemini"""

        img = Image.open(image_path)

        prompt = """Analyze this food image and provide detailed nutritional information.

Return a JSON object with the following structure:
{
    "description": "Brief description of the food/meal",
    "calories": <number>,
    "protein": <number in grams>,
    "carbs": <number in grams>,
    "fat": <number in grams>,
    "fiber": <number in grams>,
    "sugar": <number in grams>,
    "meal_type": "breakfast|lunch|dinner|snack"
}

Be as accurate as possible with portion estimation. If you're unsure, provide your best estimate.
Only respond with the JSON object, no additional text."""

        response = self.model.generate_content([prompt, img])
        response_text = response.text

        # Parse response
        try:
            # Try to extract JSON from markdown code blocks
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()

            nutrition_data = json.loads(response_text)
            return nutrition_data
        except json.JSONDecodeError:
            # Try to extract JSON from response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > start:
                nutrition_data = json.loads(response_text[start:end])
                return nutrition_data
            raise ValueError("Could not parse nutrition data from AI response")

    def analyze_text_meal(self, text):
        """Analyze text description of meal and extract nutritional information"""

        prompt = f"""The user said: "{text}"

This is about a meal they ate or are planning to eat. Extract nutritional information and meal details.

Return a JSON object with the following structure:
{{
    "description": "Brief description of the food/meal mentioned",
    "calories": <number>,
    "protein": <number in grams>,
    "carbs": <number in grams>,
    "fat": <number in grams>,
    "fiber": <number in grams>,
    "sugar": <number in grams>,
    "meal_type": "breakfast|lunch|dinner|snack"
}}

Be as accurate as possible. If specific portions aren't mentioned, assume standard portions.
Only respond with the JSON object, no additional text."""

        response = self.model.generate_content(prompt)
        response_text = response.text

        try:
            # Try to extract JSON from markdown code blocks
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()

            nutrition_data = json.loads(response_text)
            return nutrition_data
        except json.JSONDecodeError:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > start:
                nutrition_data = json.loads(response_text[start:end])
                return nutrition_data
            raise ValueError("Could not parse nutrition data from AI response")

    def parse_user_intent(self, text, user_data):
        """Parse user intent from text - stats, profile info, settings update, or meal logging"""

        prompt = f"""The user said: "{text}"

Current user settings:
- Name: {user_data.get('name', 'Unknown')}
- Height: {user_data.get('height', 0)} cm
- Weight: {user_data.get('weight', 0)} kg
- Goal: {user_data.get('goal', 'Unknown')}
- Goal Speed: {user_data.get('goal_speed', 'Unknown')}

Determine the user's intent. Options:
1. get_stats - User wants to see their eating statistics (today, week, month, year)
2. get_profile - User wants to see their profile info (weight, height, goal, etc)
3. update_setting - User wants to update weight, height, goal, or goal_speed
4. update_meal_time - User wants to change meal reminder times
5. log_meal - User wants to log a meal they ate

Return a JSON object:
{{
    "action": "get_stats|get_profile|update_setting|update_meal_time|log_meal",
    "period": "day|week|month|year|null",
    "field": "weight|height|goal|goal_speed|breakfast_time|lunch_time|dinner_time|null",
    "value": <new value or null>,
    "confidence": <0.0 to 1.0>
}}

Examples:
- "show me my stats" -> {{"action": "get_stats", "period": "day", "field": null, "value": null, "confidence": 0.95}}
- "what did I eat this week" -> {{"action": "get_stats", "period": "week", "field": null, "value": null, "confidence": 0.9}}
- "tell me the stats what I eat" -> {{"action": "get_stats", "period": "day", "field": null, "value": null, "confidence": 0.85}}
- "what's my weight?" -> {{"action": "get_profile", "period": null, "field": null, "value": null, "confidence": 0.9}}
- "show my info" -> {{"action": "get_profile", "period": null, "field": null, "value": null, "confidence": 0.95}}
- "change my weight to 75kg" -> {{"action": "update_setting", "period": null, "field": "weight", "value": 75, "confidence": 0.95}}
- "I ate pizza" -> {{"action": "log_meal", "period": null, "field": null, "value": null, "confidence": 0.9}}

Only respond with the JSON object, no additional text."""

        response = self.model.generate_content(prompt)
        response_text = response.text

        try:
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()

            intent_data = json.loads(response_text)
            return intent_data
        except json.JSONDecodeError:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > start:
                intent_data = json.loads(response_text[start:end])
                return intent_data
            return {"action": "log_meal", "period": None, "field": None, "value": None, "confidence": 0.5}

    def parse_natural_command(self, text, user_data):
        """Parse natural language commands to update user settings"""

        prompt = f"""The user said: "{text}"

Current user settings:
- Name: {user_data.get('name', 'Unknown')}
- Height: {user_data.get('height', 0)} cm
- Weight: {user_data.get('weight', 0)} kg
- Goal: {user_data.get('goal', 'Unknown')}
- Goal Speed: {user_data.get('goal_speed', 'Unknown')}

Determine if this is a command to update any settings or meal reminder times.

Return a JSON object:
{{
    "action": "update_setting|update_meal_time|none",
    "field": "weight|height|goal|goal_speed|breakfast_time|lunch_time|dinner_time|null",
    "value": <new value or null>,
    "confidence": <0.0 to 1.0>
}}

Examples:
- "Change my weight to 75kg" -> {{"action": "update_setting", "field": "weight", "value": 75, "confidence": 0.95}}
- "Set breakfast reminder to 8am" -> {{"action": "update_meal_time", "field": "breakfast_time", "value": "08:00", "confidence": 0.9}}
- "I'm 180cm tall now" -> {{"action": "update_setting", "field": "height", "value": 180, "confidence": 0.9}}

Only respond with the JSON object, no additional text."""

        response = self.model.generate_content(prompt)
        response_text = response.text

        try:
            # Try to extract JSON from markdown code blocks
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()

            command_data = json.loads(response_text)
            return command_data
        except json.JSONDecodeError:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > start:
                command_data = json.loads(response_text[start:end])
                return command_data
            return {"action": "none", "field": None, "value": None, "confidence": 0.0}
