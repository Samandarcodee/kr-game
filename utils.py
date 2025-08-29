import random
from typing import Tuple
from config import RETURN_RATE

def calculate_spin_result(bet_amount: int) -> Tuple[int, str, float]:
    """
    Spin natijasini hisoblash
    Returns: (win_amount, result_type, multiplier)
    """
    # 30% ehtimollik bilan g'alaba
    if random.random() < RETURN_RATE:
        # G'alaba multiplier: 1.5x dan 5x gacha
        multiplier = random.uniform(1.5, 5.0)
        win_amount = int(bet_amount * multiplier)
        return win_amount, "win", multiplier
    else:
        # Yutqazish
        return 0, "lose", 0.0

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
