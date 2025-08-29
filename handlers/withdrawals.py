from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from database import get_db
from models import User, Withdrawal
from keyboards import get_withdrawal_keyboard
from utils import format_number, validate_withdrawal_amount
from config import MIN_WITHDRAWAL

router = Router()

@router.message(F.text == "💸 Pul yechish")
async def withdrawal_menu(message: Message):
    """Pul yechish menyusi"""
    async for db in get_db():
        result = await db.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer("❌ Xatolik yuz berdi. /start tugmasini bosing.")
            return
        
        # Kutilayotgan chiqishlarni tekshirish
        pending_result = await db.execute(
            select(Withdrawal).where(
                Withdrawal.user_id == user.telegram_id,
                Withdrawal.status == "pending"
            )
        )
        pending_withdrawal = pending_result.scalar_one_or_none()
        
        if pending_withdrawal:
            await message.answer(
                f"""
⏳ <b>KUTILAYOTGAN CHIQISH MAVJUD</b>

💰 Miqdor: {format_number(pending_withdrawal.amount)} ⭐
📅 So'rov vaqti: {pending_withdrawal.requested_at.strftime('%d.%m.%Y %H:%M')}
🆔 So'rov ID: #{pending_withdrawal.id}

Iltimos, joriy so'rov qayta ishlanishini kuting.
Admin tez orada ko'rib chiqadi.
                """,
                parse_mode="HTML"
            )
            return
        
        withdrawal_text = f"""
💸 <b>PUL CHIQARISH BO'LIMI</b> 💸

💰 <b>Sizning balansingiz:</b> <b>{format_number(user.stars)} yulduz</b>
🎁 <b>Jami yechib olgan:</b> {format_number(user.total_withdrawn)} ⭐

📈 <b>Chiqarish shartlari:</b>
✨ Minimal miqdor: {MIN_WITHDRAWAL} ⭐
🕰 Admin tasdiqlash: 24 soat ichida
🚀 To'lov Telegram Stars orqali
🔒 Xavfsiz va ishonchli tizim

💡 <b>Muhim eslatma:</b>
So'rov yuborilgach, yulduzlar vaqtincha
bloklanadi va admin tasdiqlashini kutadi.
        """
        
        if user.stars < MIN_WITHDRAWAL:
            withdrawal_text += f"\n⚠️ <b>Balans yetarli emas!</b>\n🎯 Minimal miqdor: {MIN_WITHDRAWAL} ⭐\n💪 Ko'proq o'ynab, balansni oshiring!"
            await message.answer(withdrawal_text, parse_mode="HTML")
            return
        
        await message.answer(
            withdrawal_text,
            reply_markup=get_withdrawal_keyboard(),
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("withdraw_"))
async def process_withdrawal(callback: CallbackQuery):
    """Pul yechish jarayoni"""
    try:
        withdrawal_type = callback.data.split("_")[1]
        
        async for db in get_db():
            # Foydalanuvchini topish
            result = await db.execute(
                select(User).where(User.telegram_id == callback.from_user.id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await callback.answer("❌ Foydalanuvchi topilmadi", show_alert=True)
                return
            
            # Kutilayotgan chiqishni tekshirish
            pending_result = await db.execute(
                select(Withdrawal).where(
                    Withdrawal.user_id == user.telegram_id,
                    Withdrawal.status == "pending"
                )
            )
            pending_withdrawal = pending_result.scalar_one_or_none()
            
            if pending_withdrawal:
                await callback.answer(
                    "❌ Sizda allaqachon kutilayotgan chiqish so'rovi mavjud!",
                    show_alert=True
                )
                return
            
            # Chiqarish miqdorini aniqlash
            if withdrawal_type == "all":
                amount = user.stars
            else:
                amount = int(withdrawal_type)
            
            # Miqdorni tekshirish
            is_valid, message_text = validate_withdrawal_amount(amount, user.stars)
            if not is_valid:
                await callback.answer(message_text, show_alert=True)
                return
            
            # Yulduzlarni bloklamlash
            user.stars -= amount
            
            # Chiqish so'rovini yaratish
            withdrawal = Withdrawal(
                user_id=user.telegram_id,
                amount=amount,
                status="pending"
            )
            
            db.add(withdrawal)
            await db.commit()
            await db.refresh(withdrawal)
            
            success_text = f"""
✅ <b>CHIQISH SO'ROVI YUBORILDI!</b>

💰 Miqdor: <b>{format_number(amount)} ⭐</b>
🆔 So'rov ID: <b>#{withdrawal.id}</b>
📅 So'rov vaqti: {datetime.now().strftime('%d.%m.%Y %H:%M')}

⏳ <b>Keyingi qadamlar:</b>
1. Admin so'rovingizni ko'rib chiqadi
2. Tasdiqlangandan so'ng pul yuboriladi
3. Telegram orqali xabar olasiz

⭐ <b>Yangi balans:</b> {format_number(user.stars)} yulduz

💡 <b>Eslatma:</b> Odatda 24 soat ichida qayta ishlanadi.
            """
            
            await callback.message.edit_text(
                success_text,
                parse_mode="HTML"
            )
            await callback.answer("✅ So'rov yuborildi!")
            
    except Exception as e:
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        print(f"Withdrawal error: {e}")
