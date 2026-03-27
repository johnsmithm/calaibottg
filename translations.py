# Translation dictionaries for the bot

TRANSLATIONS = {
    'en': {
        # Commands
        'welcome_back': "Welcome back, {}! 👋\n\nSend me a photo of your meal, voice message, or text description to track it.\n\nCommands:\n/stats - View your statistics\n/settings - Update your profile\n/lang - Change language\n/help - Get help",
        'onboarding_welcome': "👋 Welcome to Calorie Tracker Bot!\n\nI'll help you track your nutrition and reach your goals.\n\nLet's get started! What's your name?",
        'whats_your_name': "What's your name?",
        'whats_your_height': "Nice to meet you, {}! 😊\n\nWhat's your height in cm?",
        'whats_your_weight': "Great! Now, what's your current weight in kg?",
        'select_goal': "What's your goal?",
        'select_goal_speed': "How quickly do you want to reach your goal?",
        'breakfast_time': "What time do you usually eat breakfast? (e.g., 08:00)",
        'lunch_time': "What time do you usually eat lunch? (e.g., 13:00)",
        'dinner_time': "What time do you usually eat dinner? (e.g., 19:00)",

        # Meal analysis
        'analyzing_meal': "🔍 Analyzing your meal...",
        'processing_voice': "🎤 Processing your voice message...",
        'save_this_meal': "Save this meal?",
        'meal_saved': "✅ Meal Saved!",
        'meal_cancelled': "❌ Meal cancelled.",

        # Buttons
        'btn_save': "✅ Save",
        'btn_edit_calories': "✏️ Edit Calories",
        'btn_edit_again': "✏️ Edit Again",
        'btn_cancel': "❌ Cancel",

        # Nutrition info
        'nutritional_info': "📊 *Nutritional Information:*",
        'meal_type': "🍴 Meal Type",
        'calories': "⚡️ Calories",
        'protein': "🥩 Protein",
        'carbs': "🍞 Carbs",
        'fat': "🥑 Fat",
        'fiber': "🌾 Fiber",
        'sugar': "🍬 Sugar",
        'ingredients': "*INGREDIENTS:*",
        'total': "*TOTAL:*",

        # Stats
        'todays_progress': "📊 *TODAY'S PROGRESS*",
        'macros_today': "*MACROS TODAY:*",
        'meals_today': "🍽 Meals today",
        'remaining': "📊 Remaining",

        # Errors
        'error_voice_unclear': "❌ Sorry, I couldn't understand the audio. Please try speaking more clearly.",
        'error_voice_service': "❌ Sorry, there was an error with the speech recognition service. Please try again later.",
        'error_voice_generic': "❌ Sorry, I couldn't process your voice message. Error: {}\n\nPlease try again or send a text/photo instead.",
        'error_analyzing': "❌ Sorry, I couldn't analyze this image. Please try again.",

        # Edit calories
        'edit_calories_prompt': "Current calories: *{} kcal*\n\nPlease send the corrected calorie value.\n\nYou can also mention:\n• What's in the photo if AI missed something\n• Portion size if different (e.g., 'actually 200g chicken')\n\nExamples:\n• 450\n• 450 kcal\n• It's 300g chicken breast not 150g",
        'updated_nutritional_info': "✅ *Updated Nutritional Information:*",
        'reanalyzing': "🔍 Re-analyzing with your feedback...",

        # Language selection
        'select_language': "🌐 Select your language:\n\n🇬🇧 English\n🇷🇴 Romanian\n🇷🇺 Russian",
        'language_changed': "✅ Language changed to English!",

        # Reminders
        'reminder_breakfast': "🌅 Good morning! Time for breakfast. Send me a photo of your meal!",
        'reminder_lunch': "🌞 Lunch time! Don't forget to log your meal.",
        'reminder_dinner': "🌙 Dinner time! Remember to track your evening meal.",
    },

    'ro': {
        # Commands
        'welcome_back': "Bine ai revenit, {}! 👋\n\nTrimite-mi o poză cu masa ta, mesaj vocal sau descriere text pentru a o înregistra.\n\nComenzi:\n/stats - Vezi statisticile\n/settings - Actualizează profilul\n/lang - Schimbă limba\n/help - Ajutor",
        'onboarding_welcome': "👋 Bine ai venit la Calorie Tracker Bot!\n\nTe voi ajuta să îți urmărești nutriția și să îți atingi obiectivele.\n\nHai să începem! Care este numele tău?",
        'whats_your_name': "Care este numele tău?",
        'whats_your_height': "Încântat de cunoștință, {}! 😊\n\nCare este înălțimea ta în cm?",
        'whats_your_weight': "Grozav! Acum, care este greutatea ta actuală în kg?",
        'select_goal': "Care este obiectivul tău?",
        'select_goal_speed': "Cât de repede vrei să îți atingi obiectivul?",
        'breakfast_time': "La ce oră mănânci de obicei micul dejun? (ex: 08:00)",
        'lunch_time': "La ce oră mănânci de obicei prânzul? (ex: 13:00)",
        'dinner_time': "La ce oră mănânci de obicei cina? (ex: 19:00)",

        # Meal analysis
        'analyzing_meal': "🔍 Analizez masa ta...",
        'processing_voice': "🎤 Procesez mesajul vocal...",
        'save_this_meal': "Salvezi această masă?",
        'meal_saved': "✅ Masă salvată!",
        'meal_cancelled': "❌ Masă anulată.",

        # Buttons
        'btn_save': "✅ Salvează",
        'btn_edit_calories': "✏️ Editează calorii",
        'btn_edit_again': "✏️ Editează din nou",
        'btn_cancel': "❌ Anulează",

        # Nutrition info
        'nutritional_info': "📊 *Informații nutriționale:*",
        'meal_type': "🍴 Tip masă",
        'calories': "⚡️ Calorii",
        'protein': "🥩 Proteine",
        'carbs': "🍞 Carbohidrați",
        'fat': "🥑 Grăsimi",
        'fiber': "🌾 Fibre",
        'sugar': "🍬 Zahăr",
        'ingredients': "*INGREDIENTE:*",
        'total': "*TOTAL:*",

        # Stats
        'todays_progress': "📊 *PROGRESUL DE AZI*",
        'macros_today': "*MACRONUTRIENȚI AZI:*",
        'meals_today': "🍽 Mese azi",
        'remaining': "📊 Rămas",

        # Errors
        'error_voice_unclear': "❌ Scuze, nu am înțeles audio-ul. Te rog vorbește mai clar.",
        'error_voice_service': "❌ Scuze, a fost o eroare cu serviciul de recunoaștere vocală. Încearcă mai târziu.",
        'error_voice_generic': "❌ Scuze, nu am putut procesa mesajul vocal. Eroare: {}\n\nÎncearcă din nou sau trimite text/poză.",
        'error_analyzing': "❌ Scuze, nu am putut analiza această imagine. Încearcă din nou.",

        # Edit calories
        'edit_calories_prompt': "Calorii actuale: *{} kcal*\n\nTe rog trimite valoarea corectată a caloriilor.\n\nPoți menționa și:\n• Ce este în poză dacă AI a ratat ceva\n• Dimensiunea porției dacă e diferită (ex: 'de fapt 200g pui')\n\nExemple:\n• 450\n• 450 kcal\n• E 300g piept de pui nu 150g",
        'updated_nutritional_info': "✅ *Informații nutriționale actualizate:*",
        'reanalyzing': "🔍 Reanalizez cu feedback-ul tău...",

        # Language selection
        'select_language': "🌐 Alege limba:\n\n🇬🇧 Engleză\n🇷🇴 Română\n🇷🇺 Rusă",
        'language_changed': "✅ Limba schimbată în Română!",

        # Reminders
        'reminder_breakfast': "🌅 Bună dimineața! E timpul pentru micul dejun. Trimite-mi o poză cu masa ta!",
        'reminder_lunch': "🌞 E ora prânzului! Nu uita să înregistrezi masa.",
        'reminder_dinner': "🌙 E ora cinei! Amintește-ți să îți urmărești masa de seară.",
    },

    'ru': {
        # Commands
        'welcome_back': "С возвращением, {}! 👋\n\nОтправьте мне фото вашей еды, голосовое сообщение или текстовое описание для отслеживания.\n\nКоманды:\n/stats - Статистика\n/settings - Настройки\n/lang - Сменить язык\n/help - Помощь",
        'onboarding_welcome': "👋 Добро пожаловать в Calorie Tracker Bot!\n\nЯ помогу вам отслеживать питание и достигать целей.\n\nДавайте начнем! Как вас зовут?",
        'whats_your_name': "Как вас зовут?",
        'whats_your_height': "Приятно познакомиться, {}! 😊\n\nКакой ваш рост в см?",
        'whats_your_weight': "Отлично! Теперь, какой ваш текущий вес в кг?",
        'select_goal': "Какая ваша цель?",
        'select_goal_speed': "Как быстро вы хотите достичь цели?",
        'breakfast_time': "Во сколько вы обычно завтракаете? (напр: 08:00)",
        'lunch_time': "Во сколько вы обычно обедаете? (напр: 13:00)",
        'dinner_time': "Во сколько вы обычно ужинаете? (напр: 19:00)",

        # Meal analysis
        'analyzing_meal': "🔍 Анализирую вашу еду...",
        'processing_voice': "🎤 Обрабатываю голосовое сообщение...",
        'save_this_meal': "Сохранить это блюдо?",
        'meal_saved': "✅ Блюдо сохранено!",
        'meal_cancelled': "❌ Блюдо отменено.",

        # Buttons
        'btn_save': "✅ Сохранить",
        'btn_edit_calories': "✏️ Изменить калории",
        'btn_edit_again': "✏️ Изменить снова",
        'btn_cancel': "❌ Отмена",

        # Nutrition info
        'nutritional_info': "📊 *Пищевая ценность:*",
        'meal_type': "🍴 Тип приёма пищи",
        'calories': "⚡️ Калории",
        'protein': "🥩 Белки",
        'carbs': "🍞 Углеводы",
        'fat': "🥑 Жиры",
        'fiber': "🌾 Клетчатка",
        'sugar': "🍬 Сахар",
        'ingredients': "*ИНГРЕДИЕНТЫ:*",
        'total': "*ИТОГО:*",

        # Stats
        'todays_progress': "📊 *ПРОГРЕСС СЕГОДНЯ*",
        'macros_today': "*МАКРОНУТРИЕНТЫ СЕГОДНЯ:*",
        'meals_today': "🍽 Приёмов пищи сегодня",
        'remaining': "📊 Осталось",

        # Errors
        'error_voice_unclear': "❌ Извините, не удалось распознать аудио. Пожалуйста, говорите четче.",
        'error_voice_service': "❌ Извините, произошла ошибка с сервисом распознавания речи. Попробуйте позже.",
        'error_voice_generic': "❌ Извините, не удалось обработать голосовое сообщение. Ошибка: {}\n\nПопробуйте снова или отправьте текст/фото.",
        'error_analyzing': "❌ Извините, не удалось проанализировать это изображение. Попробуйте снова.",

        # Edit calories
        'edit_calories_prompt': "Текущие калории: *{} ккал*\n\nПожалуйста, отправьте исправленное значение калорий.\n\nВы также можете указать:\n• Что на фото, если AI что-то пропустил\n• Размер порции, если отличается (напр: 'на самом деле 200г курицы')\n\nПримеры:\n• 450\n• 450 ккал\n• Это 300г куриной грудки, а не 150г",
        'updated_nutritional_info': "✅ *Обновленная пищевая ценность:*",
        'reanalyzing': "🔍 Повторный анализ с вашими уточнениями...",

        # Language selection
        'select_language': "🌐 Выберите язык:\n\n🇬🇧 Английский\n🇷🇴 Румынский\n🇷🇺 Русский",
        'language_changed': "✅ Язык изменен на Русский!",

        # Reminders
        'reminder_breakfast': "🌅 Доброе утро! Время завтрака. Отправьте мне фото вашей еды!",
        'reminder_lunch': "🌞 Время обеда! Не забудьте записать прием пищи.",
        'reminder_dinner': "🌙 Время ужина! Не забудьте отследить вечерний прием пищи.",
    }
}

def t(key, lang='en', **kwargs):
    """Get translation for a key in the specified language"""
    text = TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, TRANSLATIONS['en'].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except:
            return text
    return text

def get_user_lang(user):
    """Get user's language, defaulting to 'en'"""
    if user and isinstance(user, dict):
        return user.get('language', 'en')
    return 'en'

# Language code mapping for speech recognition
SPEECH_LANG_CODES = {
    'en': 'en-US',
    'ro': 'ro-RO',
    'ru': 'ru-RU'
}
