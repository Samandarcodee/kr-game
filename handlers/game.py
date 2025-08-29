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
╔═══════════════════════════╗
║     🎰 <b>SLOT MACHINE</b> 🎰      ║
║       <b>PREMIUM O'YIN</b>         ║
╚═══════════════════════════╝

💰 <b>Joriy balans:</b> {format_number(user.stars)} ⭐

🎯 <b>O'yin qoidalari:</b>
┌─────────────────────────┐
│ 💸 1 ⭐ = 1 spin        │
│ 🎊 40% yutuq ehtimoli   │
│ 🏆 3 ta bir xil = WIN!  │
└─────────────────────────┘

💎 <b>Yutuq jadvali:</b>
🥇 💎💎💎 = x10 (JACKPOT!)
🥈 ⭐⭐⭐ = x8 (Yulduz)
🥉 🔔🔔🔔 = x6 (Qo'ng'iroq)
   🍒🍒🍒 = x5 (Gilos)
   🍇🍇🍇 = x4 (Uzum)
   🍋🍋🍋 = x3 (Limon)
   🍊🍊🍊 = x2.5 (Apelsin)
   🍎🍎🍎 = x2 (Olma)

📈 <b>Admin foydasi:</b> 60%
🎁 <b>Sizning ulushingiz:</b> 40%

🍀 Omadingizni sinab ko'ring!
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
            win_amount, result_type, multiplier, symbols = calculate_spin_result(bet_amount)
            
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
                user.stars,
                symbols
            )
            
    except Exception as e:
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        print(f"Spin error: {e}")

async def show_spin_result(callback, bet_amount, win_amount, result_type, multiplier, new_balance, symbols):
    """Spin natijasini chiroyli ko'rsatish"""
    
    # Animatsiyali spin natijasi
    symbols_display = f"🎰 【 {symbols[0]} 】【 {symbols[1]} 】【 {symbols[2]} 】 🎰"
    
    if result_type == "win":
        # Yutish emoji va ranglar
        win_emojis = ["🎉", "🥳", "🎊", "💰", "✨", "🌟"]
        emoji = random.choice(win_emojis)
        
        result_text = f"""
╔═══════════════════════════╗
║   🎊 <b>TABRIKLAYMIZ!</b> 🎊         ║
║        <b>SIZ YUTDINGIZ!</b>         ║
╚═══════════════════════════╝

{symbols_display}

🏆 <b>JACKPOT!</b> 3 ta bir xil belgi! {emoji}

┌─────────────────────────┐
│ 💰 Tikdingiz: {bet_amount} ⭐
│ 🎉 Yutdingiz: <b>{format_number(win_amount)} ⭐</b>
│ 📈 Multiplier: <b>x{multiplier:.1f}</b>
│ 💸 Sof foyda: <b>+{format_number(win_amount - bet_amount)} ⭐</b>
└─────────────────────────┘

⭐ <b>Yangi balans:</b> {format_number(new_balance)} yulduz

{emoji} Omadingiz davom etsin! Yana o'ynang! {emoji}
        """
    else:
        # Yutqazish emoji
        lose_emojis = ["😔", "💔", "😢", "🤷‍♂️"]
        emoji = random.choice(lose_emojis)
        
        result_text = f"""
╔═══════════════════════════╗
║      {emoji} <b>BU SAFAR...</b> {emoji}         ║
║       <b>YUTQAZDINGIZ</b>          ║
╚═══════════════════════════╝

{symbols_display}

💭 Bir xil belgilar chiqmadi...

┌─────────────────────────┐
│ 💰 Tikdingiz: {bet_amount} ⭐
│ 📉 Yo'qotdingiz: -{bet_amount} ⭐
│ 🎯 Ehtimollik: 40% yutuq
└─────────────────────────┘

⭐ <b>Yangi balans:</b> {format_number(new_balance)} yulduz

🍀 Keyingi safar omad sizga yuz beradi!
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
🎰 <b>SLOT MACHINE O'YIN</b>

⭐ Joriy balans: <b>{format_number(user.stars)} yulduz</b>

Yana spin qilmoqchimisiz? Har bir spin 1 ⭐
        """
        
        await callback.message.edit_text(
            game_text,
            reply_markup=get_spin_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
