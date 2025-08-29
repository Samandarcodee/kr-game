from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from database import get_db
from models import User
from keyboards import get_main_menu_keyboard, get_support_keyboard
from utils import format_number
from config import ADMIN_IDS

router = Router()

class SupportStates(StatesGroup):
    waiting_for_message = State()

@router.message(F.text == "🆘 Yordam")
async def support_menu(message: Message):
    """Yordam bo'limi"""
    async for db in get_db():
        result = await db.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer("❌ Xatolik yuz berdi. /start tugmasini bosing.")
            return
        
        support_text = f"""
🆘 <b>YORDAM VA QUVVATLASH</b> 🆘

👋 Salom, {user.first_name}!

💬 <b>Admin bilan bog'lanish:</b>
Har qanday savol, muammo yoki takliflaringiz 
bo'lsa, biz bilan bog'laning!

📞 <b>Qanday yordam beramiz:</b>
🔧 Texnik muammolar
💰 To'lov va chiqarish masalalari
🎮 O'yin qoidalari tushuntirish
💡 Takliflar va shikoyatlar

⚡ <b>Tez javob:</b>
Barcha xabarlar to'g'ridan-to'g'ri adminlarga 
yuboriladi va tez orada javob beriladi.

📝 <b>"Admin bilan yozishish" tugmasini bosib, 
xabaringizni yuboring!</b>
        """
        
        await message.answer(
            support_text,
            reply_markup=get_support_keyboard(),
            parse_mode="HTML"
        )

@router.callback_query(F.data == "contact_admin")
async def start_admin_chat(callback: CallbackQuery, state: FSMContext):
    """Admin bilan yozishishni boshlash"""
    await callback.message.edit_text(
        """
💬 <b>ADMIN BILAN YOZISHISH</b>

📝 Savolingiz, muammo yoki taklifingizni 
yozing. Xabar to'g'ridan-to'g'ri adminlarga 
yuboriladi.

⚡ Admin tez orada javob beradi.

🔙 Bekor qilish uchun /cancel yozing.
        """,
        parse_mode="HTML"
    )
    
    await state.set_state(SupportStates.waiting_for_message)
    await callback.answer()

@router.message(SupportStates.waiting_for_message)
async def handle_user_message(message: Message, state: FSMContext):
    """Foydalanuvchi xabarini adminlarga yuborish"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer(
            "❌ Bekor qilindi.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    async for db in get_db():
        result = await db.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer("❌ Xatolik yuz berdi.")
            return
    
    # Foydalanuvchiga tasdiqlash
    await message.answer(
        """
✅ <b>XABAR YUBORILDI!</b>

📤 Sizning xabaringiz adminlarga yuborildi.
📞 Admin tez orada javob beradi.

🏠 Asosiy menyuga qaytish uchun tugmani bosing.
        """,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
    
    # Adminlarga xabar yuborish
    admin_message = f"""
🆘 <b>YANGI YORDAM SO'ROVI</b>

👤 <b>Foydalanuvchi:</b> {user.first_name}
🆔 <b>ID:</b> {user.telegram_id}
📱 <b>Username:</b> @{user.username or 'Yoq'}
💰 <b>Balans:</b> {format_number(user.stars)} ⭐

💬 <b>Xabar:</b>
{message.text}

📅 <b>Vaqt:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}

📤 <b>Javob berish uchun:</b>
/reply {user.telegram_id} [javob matni]
    """
    
    # Barcha adminlarga yuborish
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                chat_id=admin_id,
                text=admin_message,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Admin {admin_id} ga xabar yuborishda xatolik: {e}")
    
    await state.clear()

@router.message(F.text.startswith("/reply"))
async def admin_reply(message: Message):
    """Admin javob berish"""
    if message.from_user.id not in ADMIN_IDS:
        return
    
    try:
        parts = message.text.split(" ", 2)
        if len(parts) < 3:
            await message.answer(
                "❌ Noto'g'ri format!\n"
                "To'g'ri format: /reply [user_id] [javob matni]"
            )
            return
        
        user_id = int(parts[1])
        reply_text = parts[2]
        
        # Foydalanuvchiga javob yuborish
        reply_message = f"""
📞 <b>ADMIN JAVOBI</b>

💬 <b>Javob:</b>
{reply_text}

📅 <b>Vaqt:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}

💡 Yana savol bo'lsa, "🆘 Yordam" bo'limidan yozing!
        """
        
        await message.bot.send_message(
            chat_id=user_id,
            text=reply_message,
            parse_mode="HTML"
        )
        
        await message.answer("✅ Javob yuborildi!")
        
    except ValueError:
        await message.answer("❌ User ID raqam bo'lishi kerak!")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery):
    """Asosiy menyuga qaytish"""
    await callback.message.delete()
    await callback.message.answer(
        "🏠 Asosiy menyu",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()