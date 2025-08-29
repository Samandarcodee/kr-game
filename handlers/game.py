import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User, SpinResult, Transaction
from keyboards import get_spin_keyboard
from utils import calculate_spin_result, format_number, get_spin_emoji

router = Router()

@router.message(F.text == "🎰 O'yin o'ynash")
async def game_menu(message: Message):
    """O'yin menyusi"""
    async for db in get_db():
        result = await db.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer("❌ Xatolik yuz berdi. /start tugmasini bosing.")
            return
        
        game_text = f"""
🎰 <b>YULDUZLI O'YIN</b>

⭐ Joriy balans: <b>{format_number(user.stars)} yulduz</b>

🎯 <b>O'yin qoidalari:</b>
• Har bir spinda 30% g'alaba imkoniyati
• G'alaba qilsangiz 1.5x dan 5x gacha ko'payish
• Adolatli va tasodifiy natijalar

💡 <b>Spin narxlari:</b>
• 10 ⭐ - Oddiy spin
• 25 ⭐ - O'rtacha spin  
• 50 ⭐ - Katta spin

Omadingizni sinab ko'ring! 🍀
        """
        
        await message.answer(
            game_text,
            reply_markup=get_spin_keyboard(),
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("spin_"))
async def process_spin(callback: CallbackQuery):
    """Spin jarayoni"""
    try:
        bet_amount = int(callback.data.split("_")[1])
        
        async for db in get_db():
            # Foydalanuvchini topish
            result = await db.execute(
                select(User).where(User.telegram_id == callback.from_user.id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await callback.answer("❌ Foydalanuvchi topilmadi", show_alert=True)
                return
            
            # Balansni tekshirish
            if user.stars < bet_amount:
                await callback.answer(
                    f"❌ Balansda yetarli yulduz yo'q!\n"
                    f"Kerak: {bet_amount} ⭐\n"
                    f"Mavjud: {user.stars} ⭐",
                    show_alert=True
                )
                return
            
            # Spin natijasini hisoblash
            win_amount, result_type, multiplier = calculate_spin_result(bet_amount)
            
            # Balansni yangilash
            user.stars -= bet_amount
            
            if result_type == "win":
                user.stars += win_amount
                user.total_won += win_amount
            
            # Spin natijasini saqlash
            spin_result = SpinResult(
                user_id=user.telegram_id,
                bet_amount=bet_amount,
                win_amount=win_amount,
                spin_result=result_type,
                multiplier=multiplier
            )
            
            # Tranzaksiyani saqlash
            if result_type == "win":
                transaction = Transaction(
                    user_id=user.telegram_id,
                    transaction_type="win",
                    amount=win_amount,
                    description=f"O'yinda yutildi: {win_amount} ⭐ (x{multiplier:.2f})"
                )
                db.add(transaction)
            
            db.add(spin_result)
            await db.commit()
            
            # Natijani ko'rsatish
            await show_spin_result(
                callback, 
                bet_amount, 
                win_amount, 
                result_type, 
                multiplier, 
                user.stars
            )
            
    except Exception as e:
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        print(f"Spin error: {e}")

async def show_spin_result(callback, bet_amount, win_amount, result_type, multiplier, new_balance):
    """Spin natijasini ko'rsatish"""
    emoji = get_spin_emoji(result_type)
    
    if result_type == "win":
        result_text = f"""
{emoji} <b>TABRIKLAYMIZ! SIZ YUTDINGIZ!</b> {emoji}

🎰 <b>Spin natijalari:</b>
💰 Pul tikdingiz: {format_number(bet_amount)} ⭐
🎉 Yutdingiz: <b>{format_number(win_amount)} ⭐</b>
📈 Ko'payish: <b>x{multiplier:.2f}</b>
💸 Foyda: <b>+{format_number(win_amount - bet_amount)} ⭐</b>

⭐ <b>Yangi balans:</b> {format_number(new_balance)} yulduz

Yana o'ynaysizmi? 🎲
        """
    else:
        result_text = f"""
{emoji} <b>AFSUSKI, BU SAFAR YUTQAZDINGIZ</b> {emoji}

🎰 <b>Spin natijalari:</b>
💰 Pul tikdingiz: {format_number(bet_amount)} ⭐
💔 Natija: Yutqazish
📉 Yo'qotish: -{format_number(bet_amount)} ⭐

⭐ <b>Yangi balans:</b> {format_number(new_balance)} yulduz

Yana urinib ko'ring! Omad sizga yuz beradi! 🍀
        """
    
    await callback.message.edit_text(
        result_text,
        reply_markup=get_spin_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "spin_again")
async def spin_again(callback: CallbackQuery):
    """Yana spin qilish"""
    async for db in get_db():
        result = await db.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await callback.answer("❌ Foydalanuvchi topilmadi", show_alert=True)
            return
        
        game_text = f"""
🎰 <b>YULDUZLI O'YIN</b>

⭐ Joriy balans: <b>{format_number(user.stars)} yulduz</b>

Qaysi miqdorda spin qilmoqchisiz?
        """
        
        await callback.message.edit_text(
            game_text,
            reply_markup=get_spin_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
