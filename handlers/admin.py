from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from database import get_db
from models import User, Transaction, Withdrawal, SpinResult
from keyboards import get_admin_keyboard, get_withdrawal_approval_keyboard
from config import ADMIN_IDS
from utils import format_number

router = Router()

def is_admin(user_id: int) -> bool:
    """Admin ekanligini tekshirish"""
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Admin panel"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Sizda admin huquqlari yo'q!")
        return
    
    async for db in get_db():
        # Asosiy statistika
        total_users = await db.scalar(select(func.count(User.id)))
        total_deposits = await db.scalar(select(func.sum(User.total_deposited))) or 0
        total_withdrawals = await db.scalar(select(func.sum(User.total_withdrawn))) or 0
        pending_withdrawals = await db.scalar(
            select(func.count(Withdrawal.id)).where(Withdrawal.status == "pending")
        ) or 0
        
        admin_text = f"""
👑 <b>ADMIN PANEL</b>

📊 <b>Asosiy statistika:</b>
👥 Jami foydalanuvchilar: {total_users}
💰 Jami kirimlar: {format_number(total_deposits)} ⭐
💸 Jami chiqimlar: {format_number(total_withdrawals)} ⭐
⏳ Kutilayotgan chiqishlar: {pending_withdrawals}

💰 <b>Daromad:</b> {format_number(total_deposits - total_withdrawals)} ⭐

Quyidagi tugmalardan birini tanlang:
        """
        
        await message.answer(
            admin_text,
            reply_markup=get_admin_keyboard(),
            parse_mode="HTML"
        )

@router.callback_query(F.data == "admin_stats")
async def admin_statistics(callback: CallbackQuery):
    """Batafsil statistika"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat berilmagan!", show_alert=True)
        return
    
    async for db in get_db():
        # Bugungi statistika
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # Bugungi foydalanuvchilar
        today_users = await db.scalar(
            select(func.count(User.id)).where(
                func.date(User.created_at) == today
            )
        ) or 0
        
        # Bugungi kirimlar
        today_deposits_result = await db.execute(
            select(func.sum(Transaction.amount)).where(
                Transaction.transaction_type == "purchase",
                func.date(Transaction.created_at) == today
            )
        )
        today_deposits = today_deposits_result.scalar() or 0
        
        # Bugungi spinlar
        today_spins = await db.scalar(
            select(func.count(SpinResult.id)).where(
                func.date(SpinResult.created_at) == today
            )
        ) or 0
        
        # Eng faol foydalanuvchilar
        top_users_result = await db.execute(
            select(User.first_name, User.total_deposited)
            .order_by(desc(User.total_deposited))
            .limit(5)
        )
        top_users = top_users_result.all()
        
        stats_text = f"""
📊 <b>BATAFSIL STATISTIKA</b>

📅 <b>Bugungi ma'lumotlar:</b>
👥 Yangi foydalanuvchilar: {today_users}
💰 Bugungi kirimlar: {format_number(today_deposits)} ⭐
🎰 Bugungi spinlar: {today_spins}

🏆 <b>TOP 5 FOYDALANUVCHI:</b>
        """
        
        for i, (name, deposited) in enumerate(top_users, 1):
            stats_text += f"{i}. {name}: {format_number(deposited)} ⭐\n"
        
        await callback.message.edit_text(
            stats_text,
            reply_markup=get_admin_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()

@router.callback_query(F.data == "admin_withdrawals")
async def admin_withdrawals(callback: CallbackQuery):
    """Chiqarish so'rovlari"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat berilmagan!", show_alert=True)
        return
    
    async for db in get_db():
        # Kutilayotgan chiqishlar
        pending_result = await db.execute(
            select(Withdrawal)
            .where(Withdrawal.status == "pending")
            .order_by(Withdrawal.requested_at)
            .limit(10)
        )
        pending_withdrawals = pending_result.scalars().all()
        
        if not pending_withdrawals:
            await callback.message.edit_text(
                "📋 <b>CHIQARISH SO'ROVLARI</b>\n\n"
                "✅ Hozirda kutilayotgan so'rovlar yo'q",
                reply_markup=get_admin_keyboard(),
                parse_mode="HTML"
            )
            await callback.answer()
            return
        
        withdrawals_text = "📋 <b>KUTILAYOTGAN CHIQISHLAR</b>\n\n"
        
        for withdrawal in pending_withdrawals:
            # Foydalanuvchi ma'lumotlarini olish
            user_result = await db.execute(
                select(User).where(User.telegram_id == withdrawal.user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if user:
                withdrawals_text += f"""
💸 <b>So'rov #{withdrawal.id}</b>
👤 Foydalanuvchi: {user.first_name}
🆔 ID: {user.telegram_id}
💰 Miqdor: {format_number(withdrawal.amount)} ⭐
📅 So'rov vaqti: {withdrawal.requested_at.strftime('%d.%m.%Y %H:%M')}
{"─" * 30}
                """
        
        await callback.message.edit_text(
            withdrawals_text,
            parse_mode="HTML"
        )
        
        # Har bir so'rov uchun tugma
        if pending_withdrawals:
            withdrawal = pending_withdrawals[0]  # Birinchi so'rov
            await callback.message.edit_reply_markup(
                reply_markup=get_withdrawal_approval_keyboard(withdrawal.id)
            )
        
        await callback.answer()

@router.callback_query(F.data.startswith("approve_withdrawal_"))
async def approve_withdrawal(callback: CallbackQuery):
    """Chiqishni tasdiqlash"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat berilmagan!", show_alert=True)
        return
    
    try:
        withdrawal_id = int(callback.data.split("_")[2])
        
        async for db in get_db():
            # Chiqish so'rovini topish
            withdrawal_result = await db.execute(
                select(Withdrawal).where(Withdrawal.id == withdrawal_id)
            )
            withdrawal = withdrawal_result.scalar_one_or_none()
            
            if not withdrawal or withdrawal.status != "pending":
                await callback.answer("❌ So'rov topilmadi yoki allaqachon qayta ishlangan", show_alert=True)
                return
            
            # Foydalanuvchini topish
            user_result = await db.execute(
                select(User).where(User.telegram_id == withdrawal.user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                await callback.answer("❌ Foydalanuvchi topilmadi", show_alert=True)
                return
            
            # Chiqishni tasdiqlash
            withdrawal.status = "approved"
            withdrawal.processed_at = datetime.utcnow()
            withdrawal.processed_by = callback.from_user.id
            
            # Foydalanuvchi statistikasini yangilash
            user.total_withdrawn += withdrawal.amount
            
            # Tranzaksiya yaratish
            transaction = Transaction(
                user_id=user.telegram_id,
                transaction_type="withdrawal",
                amount=-withdrawal.amount,
                description=f"Pul yechish tasdiqlandi: {withdrawal.amount} ⭐"
            )
            
            db.add(transaction)
            await db.commit()
            
            # Foydalanuvchiga xabar yuborish
            try:
                await callback.bot.send_message(
                    user.telegram_id,
                    f"""
✅ <b>CHIQISH TASDIQLANDI!</b>

💰 Miqdor: {format_number(withdrawal.amount)} ⭐
📅 Tasdiqlangan vaqt: {datetime.now().strftime('%d.%m.%Y %H:%M')}
🆔 So'rov ID: #{withdrawal.id}

Pul sizning hisobingizga tashlab berildi! 💳
                    """,
                    parse_mode="HTML"
                )
            except:
                pass  # Foydalanuvchi botni to'xtatgan bo'lsa
            
            await callback.message.edit_text(
                f"✅ Chiqish #{withdrawal_id} tasdiqlandi!\n"
                f"💰 Miqdor: {format_number(withdrawal.amount)} ⭐\n"
                f"👤 Foydalanuvchi: {user.first_name}",
                reply_markup=get_admin_keyboard(),
                parse_mode="HTML"
            )
            
            await callback.answer("✅ Chiqish tasdiqlandi!")
            
    except Exception as e:
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        print(f"Withdrawal approval error: {e}")

@router.callback_query(F.data.startswith("reject_withdrawal_"))
async def reject_withdrawal(callback: CallbackQuery):
    """Chiqishni rad etish"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat berilmagan!", show_alert=True)
        return
    
    try:
        withdrawal_id = int(callback.data.split("_")[2])
        
        async for db in get_db():
            # Chiqish so'rovini topish
            withdrawal_result = await db.execute(
                select(Withdrawal).where(Withdrawal.id == withdrawal_id)
            )
            withdrawal = withdrawal_result.scalar_one_or_none()
            
            if not withdrawal or withdrawal.status != "pending":
                await callback.answer("❌ So'rov topilmadi yoki allaqachon qayta ishlangan", show_alert=True)
                return
            
            # Foydalanuvchini topish
            user_result = await db.execute(
                select(User).where(User.telegram_id == withdrawal.user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                await callback.answer("❌ Foydalanuvchi topilmadi", show_alert=True)
                return
            
            # Chiqishni rad etish
            withdrawal.status = "rejected"
            withdrawal.processed_at = datetime.utcnow()
            withdrawal.processed_by = callback.from_user.id
            withdrawal.admin_note = "Admin tomonidan rad etildi"
            
            # Yulduzlarni qaytarish
            user.stars += withdrawal.amount
            
            await db.commit()
            
            # Foydalanuvchiga xabar yuborish
            try:
                await callback.bot.send_message(
                    user.telegram_id,
                    f"""
❌ <b>CHIQISH RAD ETILDI</b>

💰 Miqdor: {format_number(withdrawal.amount)} ⭐
📅 Rad etilgan vaqt: {datetime.now().strftime('%d.%m.%Y %H:%M')}
🆔 So'rov ID: #{withdrawal.id}

⭐ Yulduzlar hisobingizga qaytarildi.
Yana urinib ko'rishingiz mumkin.
                    """,
                    parse_mode="HTML"
                )
            except:
                pass
            
            await callback.message.edit_text(
                f"❌ Chiqish #{withdrawal_id} rad etildi!\n"
                f"💰 Miqdor: {format_number(withdrawal.amount)} ⭐\n"
                f"👤 Foydalanuvchi: {user.first_name}",
                reply_markup=get_admin_keyboard(),
                parse_mode="HTML"
            )
            
            await callback.answer("❌ Chiqish rad etildi!")
            
    except Exception as e:
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        print(f"Withdrawal rejection error: {e}")

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    """Foydalanuvchilar ro'yxati"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat berilmagan!", show_alert=True)
        return
    
    async for db in get_db():
        # Eng faol foydalanuvchilar
        users_result = await db.execute(
            select(User)
            .order_by(desc(User.total_deposited))
            .limit(20)
        )
        users = users_result.scalars().all()
        
        users_text = "👥 <b>FOYDALANUVCHILAR RO'YXATI</b>\n\n"
        
        for i, user in enumerate(users, 1):
            status = "🚫 Bloklangan" if user.is_banned else "✅ Faol"
            users_text += f"""
{i}. <b>{user.first_name}</b>
🆔 ID: {user.telegram_id}
⭐ Balans: {format_number(user.stars)}
💰 Jami kiritgan: {format_number(user.total_deposited)}
📅 Ro'yxatdan: {user.created_at.strftime('%d.%m.%Y')}
📊 Status: {status}
{"─" * 25}
        """
        
        await callback.message.edit_text(
            users_text,
            reply_markup=get_admin_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
