from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from database import get_db
from models import User
from keyboards import get_main_menu_keyboard, get_referral_keyboard
from utils import format_number
from config import BOT_USERNAME

router = Router()

@router.message(F.text == "👥 Do'stlarni taklif qilish")
async def referral_menu(message: Message):
    """Referal menyu"""
    async for db in get_db():
        result = await db.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer("❌ Xatolik yuz berdi. /start tugmasini bosing.")
            return
        
        # Referal link yaratish
        referral_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user.telegram_id}"
        
        referral_text = f"""
👥 <b>DO'STLARNI TAKLIF QILING!</b> 👥

🎁 <b>Sizning natijalaringiz:</b>
🔗 Taklif qilganlar: <b>{user.total_referrals}</b> kishi
💰 Referal orqali topgan: <b>{format_number(user.referral_earnings)}</b> ⭐

🚀 <b>Qanday ishlaydi:</b>
1️⃣ Do'stlaringizga referal linkingizni yuboring
2️⃣ Ular bot orqali yulduz sotib olib o'ynashadi
3️⃣ Siz har biridan <b>5 ⭐ bonus</b> olasiz!

💎 <b>Afzalliklar:</b>
✨ Cheksiz do'stlar taklif qilishingiz mumkin
🎯 Har bir faol do'st uchun 5 yulduz
🔄 Doimiy daromad manbai
💸 Bonuslarni istalgan vaqt chiqarib olish

🔗 <b>Sizning referal linkingiz:</b>
<code>{referral_link}</code>

📱 <b>Do'stlaringizga ayting:</b>
"Menga qo'shiling va bepul yulduzlar oling! 🌟"
        """
        
        await message.answer(
            referral_text,
            reply_markup=get_referral_keyboard(referral_link),
            parse_mode="HTML"
        )

@router.callback_query(F.data == "copy_referral_link")
async def copy_referral_link(callback: CallbackQuery):
    """Referal linkni nusxalash"""
    async for db in get_db():
        result = await db.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await callback.answer("❌ Xatolik yuz berdi.", show_alert=True)
            return
        
        referral_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user.telegram_id}"
        
        await callback.message.answer(
            f"🔗 <b>Referal linkingiz:</b>\n\n"
            f"<code>{referral_link}</code>\n\n"
            f"📋 Linkni nusxalab, do'stlaringizga yuboring!",
            parse_mode="HTML"
        )
        
        await callback.answer("✅ Link yuqorida!", show_alert=False)

async def process_referral_bonus(referrer_id: int, new_user_id: int):
    """Referal bonusini berish"""
    async for db in get_db():
        try:
            # Referal qiluvchini topish
            result = await db.execute(
                select(User).where(User.telegram_id == referrer_id)
            )
            referrer = result.scalar_one_or_none()
            
            if not referrer:
                return
            
            # Yangi foydalanuvchini tekshirish
            new_user_result = await db.execute(
                select(User).where(User.telegram_id == new_user_id)
            )
            new_user = new_user_result.scalar_one_or_none()
            
            if not new_user:
                return
            
            # Referal bonusini berish (5 yulduz)
            bonus_amount = 5
            
            # Referal qiluvchiga bonus qo'shish
            await db.execute(
                update(User)
                .where(User.telegram_id == referrer_id)
                .values(
                    stars=User.stars + bonus_amount,
                    total_referrals=User.total_referrals + 1,
                    referral_earnings=User.referral_earnings + bonus_amount
                )
            )
            
            await db.commit()
            
            # Referal qiluvchiga xabar yuborish
            from bot import bot
            try:
                await bot.send_message(
                    chat_id=referrer_id,
                    text=f"""
🎉 <b>REFERAL BONUSI!</b> 🎉

👤 Yangi do'stingiz botga qo'shildi!
💰 Bonus: <b>{bonus_amount} ⭐</b>
🎁 Jami referal daromadingiz: <b>{format_number(referrer.referral_earnings + bonus_amount)} ⭐</b>

🚀 Yana do'stlar taklif qiling va ko'proq yulduz yutib oling!
                    """,
                    parse_mode="HTML"
                )
            except Exception as e:
                print(f"Referal bonus xabarini yuborishda xatolik: {e}")
                
        except Exception as e:
            print(f"Referal bonusini qayta ishlashda xatolik: {e}")
            await db.rollback()