from aiogram import Bot
from aiogram.types import ChatMemberStatus
from config import REQUIRED_CHANNEL_ID, REQUIRED_CHANNEL

async def check_subscription(bot: Bot, user_id: int) -> bool:
    """
    Foydalanuvchining kanalga obuna bo'lganligini tekshirish
    """
    try:
        member = await bot.get_chat_member(chat_id=REQUIRED_CHANNEL_ID, user_id=user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
    except Exception as e:
        print(f"Subscription check error: {e}")
        return False

def get_subscription_message() -> str:
    """
    Obuna xabari
    """
    return f"""
❌ <b>OBUNA BO'LISH TALAB QILINADI!</b>

Botdan foydalanish uchun quyidagi kanalga obuna bo'ling:

📢 <b>Kanal:</b> {REQUIRED_CHANNEL}

🔗 <b>Obuna bo'lish:</b>
1. Yuqoridagi kanalga o'ting
2. "Obuna bo'lish" tugmasini bosing
3. Botga qaytib, "✅ Obunani tekshirish" tugmasini bosing

💡 <b>Eslatma:</b> Obuna bo'lmasdan botdan foydalana olmaysiz!
    """

def get_subscription_keyboard():
    """
    Obuna klaviaturasi
    """
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga o'tish", url=f"https://t.me/{REQUIRED_CHANNEL[1:]}")],
            [InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subscription")]
        ]
    )
    return keyboard