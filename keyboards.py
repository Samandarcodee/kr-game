from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import STAR_PACKAGES

def get_main_menu_keyboard():
    """Asosiy menyu klaviaturasi"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎰 O'yin o'ynash")],
            [KeyboardButton(text="⭐ Yulduz sotib olish"), KeyboardButton(text="💰 Balansim")],
            [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="💸 Pul yechish")],
            [KeyboardButton(text="👥 Do'stlarni taklif qilish")],
            [KeyboardButton(text="🆘 Yordam")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard

def get_star_purchase_keyboard():
    """Yulduz sotib olish klaviaturasi"""
    buttons = []
    for stars, price in STAR_PACKAGES.items():
        buttons.append([InlineKeyboardButton(
            text=f"⭐ {stars} yulduz",
            callback_data=f"buy_stars_{stars}"
        )])
    
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_spin_keyboard():
    """Spin o'ynash klaviaturasi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎰 Spin (1 ⭐)", callback_data="spin_1")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")]
        ]
    )
    return keyboard

def get_withdrawal_keyboard():
    """Pul yechish klaviaturasi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💸 150 ⭐ yechish", callback_data="withdraw_150")],
            [InlineKeyboardButton(text="💸 300 ⭐ yechish", callback_data="withdraw_300")],
            [InlineKeyboardButton(text="💸 500 ⭐ yechish", callback_data="withdraw_500")],
            [InlineKeyboardButton(text="💸 Barchasi", callback_data="withdraw_all")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")]
        ]
    )
    return keyboard

def get_support_keyboard():
    """Yordam bo'limi klaviaturasi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Admin bilan yozishish", callback_data="contact_admin")],
            [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_main")]
        ]
    )
    return keyboard

def get_referral_keyboard(referral_link):
    """Referal bo'limi klaviaturasi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Linkni nusxalash", callback_data="copy_referral_link")],
            [InlineKeyboardButton(text="📤 Do'stlarga yuborish", url=f"https://t.me/share/url?url={referral_link}&text=Menga%20qo'shiling%20va%20bepul%20yulduzlar%20oling!%20🌟")],
            [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_main")]
        ]
    )
    return keyboard

def get_admin_keyboard():
    """Admin klaviaturasi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
            [InlineKeyboardButton(text="💸 Chiqarish so'rovlari", callback_data="admin_withdrawals")],
            [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users")],
            [InlineKeyboardButton(text="🌐 Web Admin", url="http://localhost:8000")]
        ]
    )
    return keyboard

def get_withdrawal_approval_keyboard(withdrawal_id: int):
    """Chiqarish tasdiqlash klaviaturasi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_withdrawal_{withdrawal_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_withdrawal_{withdrawal_id}")
            ],
            [InlineKeyboardButton(text="📋 Batafsil", callback_data=f"withdrawal_details_{withdrawal_id}")]
        ]
    )
    return keyboard
