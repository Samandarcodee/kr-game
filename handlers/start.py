from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User
from keyboards import get_main_menu_keyboard
from utils import get_user_rank, format_number
from utils_captcha import get_captcha_message
from utils_subscription import check_subscription, get_subscription_message, get_subscription_keyboard

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message, command: CommandObject = None):
    """Bot ishga tushganida - captcha va obuna tekshiruvi"""
    # Referal parametrini olish
    referrer_id = None
    if command and command.args and command.args.startswith('ref_'):
        try:
            referrer_id = int(command.args.replace('ref_', ''))
        except ValueError:
            referrer_id = None
    
    async for db in get_db():
        user = await get_or_create_user(db, message.from_user, referrer_id)
        
        # Agar user yangi bo'lsa yoki captcha o'tmagan bo'lsa
        if not hasattr(user, 'captcha_passed') or not user.captcha_passed:
            # Captcha ko'rsatish
            captcha_text, captcha_keyboard, correct_answer = get_captcha_message()
            
            # Captcha javobini sessionda saqlash (oddiy holatda user_id bilan)
            # Bu yerda oddiy dictda saqlaydi, real projectda Redis yoki DBda saqlash kerak
            if not hasattr(start_handler, 'captcha_answers'):
                start_handler.captcha_answers = {}
            start_handler.captcha_answers[user.telegram_id] = correct_answer
            
            await message.answer(
                captcha_text,
                reply_markup=captcha_keyboard,
                parse_mode="HTML"
            )
            return
        
        # Obuna tekshirish
        is_subscribed = await check_subscription(message.bot, message.from_user.id)
        
        if not is_subscribed:
            await message.answer(
                get_subscription_message(),
                reply_markup=get_subscription_keyboard(),
                parse_mode="HTML"
            )
            return
        
        # Agar captcha o'tgan va obuna bo'lgan bo'lsa - asosiy menyu
        await show_main_menu(message, user)

async def get_or_create_user(db: AsyncSession, telegram_user, referrer_id=None) -> User:
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
            referrer_id=referrer_id,
            last_name=telegram_user.last_name
        )
        # Yangi user uchun captcha_passed = False
        user.captcha_passed = False
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    return user

async def show_main_menu(message: Message, user: User):
    """Asosiy menyuni ko'rsatish"""
    welcome_text = f"""
🌟 <b>PREMIUM O'YIN BOTIGA XUSH KELIBSIZ!</b> 🌟

👋 Assalomu alaykum, hurmatli {user.first_name}!

✨ <b>Bizning bot orqali siz:</b>
💫 Yulduzlar sotib olishingiz
🎯 Hayajonli o'yinlar o'ynashingiz
💸 Yutgan pullaringizni chiqarib olishingiz mumkin

📈 <b>Shaxsiy ma'lumotlaringiz:</b>
🏆 Darajangiz: {get_user_rank(user.total_deposited)}
💰 Joriy balans: <b>{format_number(user.stars)}</b> yulduz
📊 Jami kiritgan: <b>{format_number(user.total_deposited)}</b> yulduz
🎁 Jami yutgan: <b>{format_number(user.total_won)}</b> yulduz

🚀 <b>O'yinni boshlash uchun quyidagi bo'limlardan birini tanlang:</b>
    """
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )

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

# Captcha callback handlerlari
@router.callback_query(F.data.startswith("captcha_"))
async def captcha_handler(callback: CallbackQuery):
    """Captcha javobini tekshirish"""
    try:
        data_parts = callback.data.split("_")
        result = data_parts[1]  # 'correct' yoki 'wrong'
        answer = int(data_parts[2])
        
        async for db in get_db():
            user = await get_or_create_user(db, callback.from_user)
            
            if result == "correct":
                # Captcha to'g'ri - obuna tekshirish
                user.captcha_passed = True
                await db.commit()
                
                # Obuna tekshirish
                is_subscribed = await check_subscription(callback.bot, callback.from_user.id)
                
                if not is_subscribed:
                    await callback.message.edit_text(
                        get_subscription_message(),
                        reply_markup=get_subscription_keyboard(),
                        parse_mode="HTML"
                    )
                    await callback.answer("✅ Captcha to'g'ri! Endi kanalga obuna bo'ling.")
                else:
                    # Captcha ham to'g'ri, obuna ham bor - asosiy menyu
                    await callback.message.delete()
                    await show_main_menu_from_callback(callback, user)
                    await callback.answer("✅ Xush kelibsiz!")
            else:
                # Captcha noto'g'ri - qayta urinish
                captcha_text, captcha_keyboard, correct_answer = get_captcha_message()
                
                # Yangi javobni saqlash
                if not hasattr(start_handler, 'captcha_answers'):
                    start_handler.captcha_answers = {}
                start_handler.captcha_answers[user.telegram_id] = correct_answer
                
                await callback.message.edit_text(
                    f"❌ Noto'g'ri javob! Qayta urinib ko'ring.\n\n{captcha_text}",
                    reply_markup=captcha_keyboard,
                    parse_mode="HTML"
                )
                await callback.answer("❌ Noto'g'ri javob, qayta urinib ko'ring!")
                
    except Exception as e:
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        print(f"Captcha error: {e}")

# Obuna tekshirish callback
@router.callback_query(F.data == "check_subscription")
async def check_subscription_handler(callback: CallbackQuery):
    """Obunani tekshirish"""
    try:
        is_subscribed = await check_subscription(callback.bot, callback.from_user.id)
        
        if is_subscribed:
            async for db in get_db():
                user = await get_or_create_user(db, callback.from_user)
                await callback.message.delete()
                await show_main_menu_from_callback(callback, user)
                await callback.answer("✅ Obuna tasdiqlandi! Xush kelibsiz!")
        else:
            await callback.answer("❌ Siz hali kanalga obuna bo'lmagansiz! Iltimos, avval obuna bo'ling.", show_alert=True)
            
    except Exception as e:
        await callback.answer("❌ Obunani tekshirishda xatolik", show_alert=True)
        print(f"Subscription check error: {e}")

async def show_main_menu_from_callback(callback: CallbackQuery, user: User):
    """Callback orqali asosiy menyuni ko'rsatish"""
    welcome_text = f"""
🌟 <b>PREMIUM O'YIN BOTIGA XUSH KELIBSIZ!</b> 🌟

👋 Assalomu alaykum, hurmatli {user.first_name}!

✨ <b>Bizning bot orqali siz:</b>
💫 Yulduzlar sotib olishingiz
🎯 Hayajonli o'yinlar o'ynashingiz
💸 Yutgan pullaringizni chiqarib olishingiz mumkin

📈 <b>Shaxsiy ma'lumotlaringiz:</b>
🏆 Darajangiz: {get_user_rank(user.total_deposited)}
💰 Joriy balans: <b>{format_number(user.stars)}</b> yulduz
📊 Jami kiritgan: <b>{format_number(user.total_deposited)}</b> yulduz
🎁 Jami yutgan: <b>{format_number(user.total_won)}</b> yulduz

🚀 <b>O'yinni boshlash uchun quyidagi bo'limlardan birini tanlang:</b>
    """
    
    await callback.message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Asosiy menyuga qaytish"""
    await callback.message.delete()
    await callback.message.answer(
        "🏠 Asosiy menyu",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()
