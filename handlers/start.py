from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User
from keyboards import get_main_menu_keyboard
from utils import get_user_rank, format_number

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    """Bot ishga tushganida"""
    async for db in get_db():
        user = await get_or_create_user(db, message.from_user)
        
        welcome_text = f"""
🎰 <b>YULDUZLI O'YIN BOTIGA XUSH KELIBSIZ!</b> 🎰

Assalomu alaykum, {user.first_name}!

Bu bot orqali siz:
⭐ Yulduz sotib olishingiz
🎰 Qiziqarli o'yinlar o'ynashingiz  
💰 Yutgan yulduzlaringizni chiqarib olishingiz mumkin

📊 <b>Sizning ma'lumotlaringiz:</b>
💎 Daraja: {get_user_rank(user.total_deposited)}
⭐ Balans: {format_number(user.stars)} yulduz
💰 Jami kiritgan: {format_number(user.total_deposited)} yulduz
🎉 Jami yutgan: {format_number(user.total_won)} yulduz

Boshlash uchun quyidagi tugmalardan birini tanlang:
        """
        
        await message.answer(
            welcome_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )

async def get_or_create_user(db: AsyncSession, telegram_user) -> User:
    """Foydalanuvchini olish yoki yaratish"""
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name or "Noma'lum",
            last_name=telegram_user.last_name
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    return user

@router.message(F.text == "💰 Balansim")
async def balance_handler(message: Message):
    """Balansni ko'rsatish"""
    async for db in get_db():
        result = await db.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer("❌ Xatolik yuz berdi. /start tugmasini bosing.")
            return
        
        balance_text = f"""
💰 <b>SIZNING BALANSIZNGIZ</b>

⭐ Joriy balans: <b>{format_number(user.stars)} yulduz</b>
💎 Daraja: <b>{get_user_rank(user.total_deposited)}</b>

📊 <b>Statistika:</b>
💰 Jami kiritgan: {format_number(user.total_deposited)} ⭐
🎉 Jami yutgan: {format_number(user.total_won)} ⭐  
💸 Jami chiqargan: {format_number(user.total_withdrawn)} ⭐

💡 <b>Eslatma:</b> Minimal chiqarish miqdori 150 ⭐
        """
        
        await message.answer(balance_text, parse_mode="HTML")

@router.message(F.text == "📊 Statistika")
async def stats_handler(message: Message):
    """Foydalanuvchi statistikasini ko'rsatish"""
    async for db in get_db():
        result = await db.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer("❌ Xatolik yuz berdi. /start tugmasini bosing.")
            return
        
        # O'yinlar statistikasi
        from models import SpinResult
        spins_result = await db.execute(
            select(SpinResult).where(SpinResult.user_id == user.telegram_id)
        )
        spins = spins_result.scalars().all()
        
        total_spins = len(spins)
        won_spins = len([s for s in spins if s.spin_result == "win"])
        win_rate = (won_spins / total_spins * 100) if total_spins > 0 else 0
        
        stats_text = f"""
📊 <b>SIZNING STATISTIKANGIZ</b>

👤 <b>Shaxsiy ma'lumotlar:</b>
🆔 ID: {user.telegram_id}
📅 Ro'yxatdan o'tgan: {user.created_at.strftime('%d.%m.%Y')}
💎 Daraja: {get_user_rank(user.total_deposited)}

💰 <b>Moliyaviy ma'lumotlar:</b>
⭐ Joriy balans: {format_number(user.stars)} yulduz
💰 Jami kiritgan: {format_number(user.total_deposited)} yulduz
🎉 Jami yutgan: {format_number(user.total_won)} yulduz
💸 Jami chiqargan: {format_number(user.total_withdrawn)} yulduz

🎰 <b>O'yin statistikasi:</b>
🎯 Jami spinlar: {total_spins}
🎉 Yutgan spinlar: {won_spins}
📈 G'alaba foizi: {win_rate:.1f}%
        """
        
        await message.answer(stats_text, parse_mode="HTML")

@router.message(F.text == "📞 Yordam")
async def help_handler(message: Message):
    """Yordam bo'limi"""
    help_text = """
📞 <b>YORDAM BO'LIMI</b>

❓ <b>Qanday o'ynash mumkin?</b>
1. Yulduz sotib oling
2. O'yin bo'limiga o'ting
3. Spin miqdorini tanlang
4. Omadingizni sinab ko'ring!

💰 <b>To'lov haqida:</b>
• Telegram Stars orqali to'lov qilinadi
• Xavfsiz va tezkor to'lov tizimi
• Turli miqdordagi paketlar mavjud

💸 <b>Pul yechish:</b>
• Minimal miqdor: 150 ⭐
• Admin tasdiqlashdan so'ng beriladi
• 24 soat ichida qayta ishlanadi

🎰 <b>O'yin qoidalari:</b>
• Har bir spinda 30% g'alaba imkoniyati
• 1.5x dan 5x gacha ko'payish
• Adolatli va tasodifiy natijalar

📞 <b>Muammo yuzaga kelsa:</b>
Admin bilan bog'laning: @admin_username
    """
    
    await message.answer(help_text, parse_mode="HTML")

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Asosiy menyuga qaytish"""
    await callback.message.delete()
    await callback.message.answer(
        "🏠 Asosiy menyu",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()
