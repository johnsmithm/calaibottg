def calculate_bmr(weight, height, age=25, gender='male'):
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation
    weight: kg
    height: cm
    age: years
    """
    if gender.lower() == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    return bmr

def calculate_tdee(bmr, activity_level='moderate'):
    """
    Calculate Total Daily Energy Expenditure
    activity_level: sedentary, light, moderate, active, very_active
    """
    activity_multipliers = {
        'sedentary': 1.2,      # Little or no exercise
        'light': 1.375,        # Light exercise 1-3 days/week
        'moderate': 1.55,      # Moderate exercise 3-5 days/week
        'active': 1.725,       # Hard exercise 6-7 days/week
        'very_active': 1.9     # Very hard exercise, physical job
    }

    multiplier = activity_multipliers.get(activity_level, 1.55)
    return bmr * multiplier

def calculate_daily_calorie_target(weight, height, goal, goal_speed, age=25, gender='male', activity_level='moderate'):
    """
    Calculate daily calorie target based on goal and speed
    goal: lose_weight, gain_weight, maintain
    goal_speed: slow, moderate, fast
    """
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity_level)

    # Define calorie deficits/surpluses
    # Slow: ~0.25kg/week, Moderate: ~0.5kg/week, Fast: ~0.75kg/week
    # 1kg fat ≈ 7700 calories

    speed_adjustments = {
        'slow': 275,      # ~0.25kg/week
        'moderate': 550,  # ~0.5kg/week
        'fast': 825       # ~0.75kg/week
    }

    adjustment = speed_adjustments.get(goal_speed, 550)

    if goal == 'lose_weight':
        target = tdee - adjustment
        # Don't go below 1200 for women, 1500 for men
        min_calories = 1500 if gender.lower() == 'male' else 1200
        target = max(target, min_calories)
    elif goal == 'gain_weight':
        target = tdee + adjustment
    else:  # maintain
        target = tdee

    return round(target)

def get_macro_distribution(calories, goal):
    """
    Calculate recommended macro distribution
    Returns: (protein_g, carbs_g, fat_g)
    """
    if goal == 'lose_weight':
        # Higher protein for weight loss (30% protein, 35% carbs, 35% fat)
        protein_cal = calories * 0.30
        carbs_cal = calories * 0.35
        fat_cal = calories * 0.35
    elif goal == 'gain_weight':
        # Higher carbs for weight gain (25% protein, 45% carbs, 30% fat)
        protein_cal = calories * 0.25
        carbs_cal = calories * 0.45
        fat_cal = calories * 0.30
    else:  # maintain
        # Balanced (25% protein, 40% carbs, 35% fat)
        protein_cal = calories * 0.25
        carbs_cal = calories * 0.40
        fat_cal = calories * 0.35

    # Convert calories to grams (protein: 4 cal/g, carbs: 4 cal/g, fat: 9 cal/g)
    protein_g = round(protein_cal / 4)
    carbs_g = round(carbs_cal / 4)
    fat_g = round(fat_cal / 9)

    return protein_g, carbs_g, fat_g
