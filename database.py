import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_name=None):
        # Use /data volume on Railway, local path otherwise
        if db_name is None:
            import os
            data_dir = '/data' if os.path.exists('/data') else '.'
            db_name = os.path.join(data_dir, 'calorie_tracker.db')
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                name TEXT NOT NULL,
                height REAL NOT NULL,
                weight REAL NOT NULL,
                goal TEXT NOT NULL,
                goal_speed TEXT NOT NULL,
                daily_calorie_target REAL NOT NULL,
                gemini_api_key TEXT,
                is_approved INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Meal times table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meal_times (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                meal_type TEXT NOT NULL,
                meal_time TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, meal_type)
            )
        ''')

        # Meals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                meal_type TEXT NOT NULL,
                calories REAL NOT NULL,
                protein REAL NOT NULL,
                carbs REAL NOT NULL,
                fat REAL NOT NULL,
                fiber REAL NOT NULL,
                sugar REAL NOT NULL,
                description TEXT,
                image_path TEXT,
                eaten_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Pending meals table (for /save /cancel flow)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pending_meals (
                user_id INTEGER PRIMARY KEY,
                meal_type TEXT NOT NULL,
                calories REAL NOT NULL,
                protein REAL NOT NULL,
                carbs REAL NOT NULL,
                fat REAL NOT NULL,
                fiber REAL NOT NULL,
                sugar REAL NOT NULL,
                description TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def create_user(self, user_id, username, name, height, weight, goal, goal_speed, daily_calorie_target, gemini_api_key=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users
            (user_id, username, name, height, weight, goal, goal_speed, daily_calorie_target, gemini_api_key, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, name, height, weight, goal, goal_speed, daily_calorie_target, gemini_api_key, datetime.now()))
        conn.commit()
        conn.close()

    def approve_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_approved = 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()

    def get_all_users(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        conn.close()
        return [dict(user) for user in users]

    def get_user_by_username(self, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    def get_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    def update_user(self, user_id, **kwargs):
        conn = self.get_connection()
        cursor = conn.cursor()

        allowed_fields = ['name', 'height', 'weight', 'goal', 'goal_speed', 'daily_calorie_target']
        updates = []
        values = []

        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                values.append(value)

        if updates:
            values.append(datetime.now())
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)}, updated_at = ? WHERE user_id = ?"
            cursor.execute(query, values)
            conn.commit()

        conn.close()

    def set_meal_time(self, user_id, meal_type, meal_time):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO meal_times (user_id, meal_type, meal_time)
            VALUES (?, ?, ?)
        ''', (user_id, meal_type, meal_time))
        conn.commit()
        conn.close()

    def get_meal_times(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT meal_type, meal_time FROM meal_times WHERE user_id = ?', (user_id,))
        times = cursor.fetchall()
        conn.close()
        return {row['meal_type']: row['meal_time'] for row in times}

    def save_pending_meal(self, user_id, meal_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO pending_meals
            (user_id, meal_type, calories, protein, carbs, fat, fiber, sugar, description, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, meal_data['meal_type'], meal_data['calories'], meal_data['protein'],
              meal_data['carbs'], meal_data['fat'], meal_data['fiber'], meal_data['sugar'],
              meal_data['description'], meal_data.get('image_path')))
        conn.commit()
        conn.close()

    def get_pending_meal(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pending_meals WHERE user_id = ?', (user_id,))
        meal = cursor.fetchone()
        conn.close()
        return dict(meal) if meal else None

    def delete_pending_meal(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM pending_meals WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()

    def save_meal(self, user_id, meal_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO meals
            (user_id, meal_type, calories, protein, carbs, fat, fiber, sugar, description, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, meal_data['meal_type'], meal_data['calories'], meal_data['protein'],
              meal_data['carbs'], meal_data['fat'], meal_data['fiber'], meal_data['sugar'],
              meal_data['description'], meal_data.get('image_path')))
        conn.commit()
        conn.close()

    def get_meals_by_date_range(self, user_id, start_date, end_date):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM meals
            WHERE user_id = ? AND eaten_at BETWEEN ? AND ?
            ORDER BY eaten_at DESC
        ''', (user_id, start_date, end_date))
        meals = cursor.fetchall()
        conn.close()
        return [dict(meal) for meal in meals]

    def get_stats(self, user_id, start_date, end_date):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                COUNT(*) as meal_count,
                SUM(calories) as total_calories,
                SUM(protein) as total_protein,
                SUM(carbs) as total_carbs,
                SUM(fat) as total_fat,
                SUM(fiber) as total_fiber,
                SUM(sugar) as total_sugar,
                AVG(calories) as avg_calories
            FROM meals
            WHERE user_id = ? AND eaten_at BETWEEN ? AND ?
        ''', (user_id, start_date, end_date))
        stats = cursor.fetchone()
        conn.close()
        return dict(stats) if stats else None
