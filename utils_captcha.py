import random
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def generate_math_captcha():
    """Matematik captcha generatsiya qilish"""
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 20)
    operation = random.choice(['+', '-'])
    
    if operation == '+':
        correct_answer = num1 + num2
        question = f"{num1} + {num2} = ?"
    else:
        # Manfiy natija chiqmasligi uchun
        if num1 < num2:
            num1, num2 = num2, num1
        correct_answer = num1 - num2
        question = f"{num1} - {num2} = ?"
    
    # 4 ta variant yaratish (1 ta to'g'ri, 3 ta noto'g'ri)
    options = [correct_answer]
    while len(options) < 4:
        wrong_answer = correct_answer + random.randint(-5, 5)
        if wrong_answer not in options and wrong_answer >= 0:
            options.append(wrong_answer)
    
    random.shuffle(options)
    return question, correct_answer, options

def get_captcha_keyboard(options, correct_answer):
    """Captcha klaviaturasi"""
    buttons = []
    for option in options:
        callback_data = f"captcha_{'correct' if option == correct_answer else 'wrong'}_{option}"
        buttons.append([InlineKeyboardButton(text=str(option), callback_data=callback_data)])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_captcha_message():
    """Captcha xabari"""
    question, correct_answer, options = generate_math_captcha()
    
    text = f"""
🤖 <b>ROBOT EMASLIGINGIZNI TASDIQLANG</b>

📊 Matematik masalani yeching:

<b>{question}</b>

⬇️ To'g'ri javobni tanlang:
    """
    
    keyboard = get_captcha_keyboard(options, correct_answer)
    return text, keyboard, correct_answer