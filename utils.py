import random
from typing import Tuple, List
from config import RETURN_RATE

# Slot machine symbols
SLOT_SYMBOLS = ["🍎", "🍊", "🍋", "🍇", "🍒", "🔔", "💎", "⭐"]

def generate_slot_result() -> List[str]:
    """3 ta symbol generatsiya qilish"""
    return [random.choice(SLOT_SYMBOLS) for _ in range(3)]

def check_win(symbols: List[str]) -> bool:
    """3 ta bir xil belgi tekshirish"""
    return len(set(symbols)) == 1

def calculate_multiplier(symbols: List[str]) -> float:
    """Symbol turiga qarab multiplier hisoblash"""
    symbol = symbols[0]
    multipliers = {
        "💎": 10.0,  # Olmos - eng yuqori
        "⭐": 8.0,   # Yulduz
        "🔔": 6.0,   # Qo'ng'iroq
        "🍒": 5.0,   # Gilos
        "🍇": 4.0,   # Uzum
        "🍋": 3.0,   # Limon
        "🍊": 2.5,   # Apelsin
        "🍎": 2.0    # Olma
    }
    return multipliers.get(symbol, 2.0)

def calculate_spin_result(bet_amount: int) -> Tuple[int, str, float, List[str]]:
    """
    Spin natijasini hisoblash - 40% g'alaba ehtimoli
    Returns: (win_amount, result_type, multiplier, symbols)
    """
    # 40% ehtimollik bilan g'alaba
    win_chance = 0.40  # 40% foydalanuvchi uchun, 60% admin foydasi
    
    if random.random() < win_chance:
        # G'alaba holati - bir xil belgilarni generatsiya qilish
        winning_symbol = random.choice(SLOT_SYMBOLS)
        symbols = [winning_symbol] * 3
        multiplier = calculate_multiplier(symbols)
        win_amount = int(bet_amount * multiplier)
        return win_amount, "win", multiplier, symbols
    else:
        # Yutqazish - turli belgilarni generatsiya qilish
        symbols = generate_mixed_symbols()
        return 0, "lose", 0.0, symbols

def generate_mixed_symbols() -> List[str]:
    """Har xil belgilar generatsiya qilish (yutqazish uchun)"""
    symbols = random.sample(SLOT_SYMBOLS, 3)
    # Agar tasodifan bir xil bo'lib qolsa, bitta o'zgartirish
    if len(set(symbols)) == 1:
        symbols[1] = random.choice([s for s in SLOT_SYMBOLS if s != symbols[0]])
    return symbols

def format_number(number: int) -> str:
    """Raqamni formatlash"""
    return f"{number:,}".replace(",", " ")

def get_spin_emoji(result_type: str) -> str:
    """Spin natijasi uchun emoji"""
    if result_type == "win":
        return random.choice(["🎉", "🥳", "🎊", "💰", "🎁"])
    else:
        return random.choice(["😢", "😔", "💔", "😞"])

def get_user_rank(total_deposited: int) -> str:
    """Foydalanuvchi darajasini aniqlash"""
    if total_deposited >= 10000:
        return "🏆 VIP"
    elif total_deposited >= 5000:
        return "💎 Premium" 
    elif total_deposited >= 1000:
        return "🥉 Bronze"
    else:
        return "🆕 Yangi"

def validate_withdrawal_amount(amount: int, user_stars: int) -> Tuple[bool, str]:
    """Chiqarish summasi to'g'riligini tekshirish"""
    if amount < 150:
        return False, "❌ Minimal chiqarish miqdori 150 ⭐"
    
    if amount > user_stars:
        return False, "❌ Balansda yetarli yulduz yo'q"
    
    return True, "✅ Chiqarish mumkin"

def generate_transaction_id() -> str:
    """Tranzaksiya ID generatsiya qilish"""
    import time
    import hashlib
    
    timestamp = str(int(time.time()))
    random_str = str(random.randint(1000, 9999))
    
    return hashlib.md5(f"{timestamp}{random_str}".encode()).hexdigest()[:8].upper()
