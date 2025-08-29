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

def calculate_spin_result(bet_amount: int, total_user_deposit: int = 0, total_user_won: int = 0) -> Tuple[int, str, float, List[str]]:
    """
    Yangi algoritm - admin 60% foyda oladi, foydalanuvchi maksimal 40% qaytaradi
    Returns: (win_amount, result_type, multiplier, symbols)
    """
    # Foydalanuvchining netto yo'qotishi
    user_net_loss = total_user_deposit - total_user_won
    
    # Admin 60% foyda olishi kerak, foydalanuvchi maksimal 40% qaytarishi mumkin
    max_user_return = total_user_deposit * 0.4
    
    # Dinamik yutish ehtimoli
    if total_user_won >= max_user_return:
        # Agar foydalanuvchi allaqachon ko'p yutgan bo'lsa - juda kam imkoniyat
        win_chance = 0.05  # 5%
    elif user_net_loss < 0:  # Foydalanuvchi foyda ko'rgan
        # Kam yutish imkoniyati
        win_chance = 0.10  # 10%
    else:
        # Oddiy yutish imkoniyati  
        win_chance = 0.20  # 20%
    
    if random.random() < win_chance:
        # G'alaba holati - bir xil belgilarni generatsiya qilish
        winning_symbol = random.choice(SLOT_SYMBOLS)
        symbols = [winning_symbol] * 3
        # Kichik multiplierlar (admin foydasini saqlash uchun)
        multipliers = [1.2, 1.5, 2.0, 2.5]
        weights = [60, 25, 12, 3]  # Kichik multiplierlar ko'proq
        
        multiplier = random.choices(multipliers, weights=weights)[0]
        win_amount = int(bet_amount * multiplier)
        
        # Agar yutish admin foydasini buzsa, kamaytirish
        potential_total_won = total_user_won + win_amount
        if potential_total_won > max_user_return:
            multiplier = 1.1  # Minimal yutish
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
