"""
Konkurs tizimi handlari
"""
import random
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, func, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User, ContestParticipant, ContestNumber, Contest
from utils import format_number
from config import ADMIN_IDS

router = Router()

@router.message(F.text == "🏆 Konkurs")
async def contest_menu(message: Message):
    """Konkurs asosiy menyusi"""
    async for db in get_db():
        # Foydalanuvchini topish
        result = await db.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer("❌ Xatolik yuz berdi. /start tugmasini bosing.")
            return
        
        # Faol konkurs mavjudligini tekshirish
        contest_result = await db.execute(
            select(Contest).where(
                Contest.is_active == True,
                Contest.end_date > datetime.utcnow()
            )
        )
        active_contest = contest_result.scalar_one_or_none()
        
        if not active_contest:
            await message.answer(
                "🏆 <b>KONKURS</b>\n\n"
                "❌ Hozirda faol konkurs yo'q.\n"
                "📢 Yangi konkurs e'lon qilinishini kuting!",
                parse_mode="HTML"
            )
            return
        
        # Foydalanuvchining konkurs holatini tekshirish
        participant_result = await db.execute(
            select(ContestParticipant).where(
                and_(
                    ContestParticipant.user_id == user.telegram_id,
                    ContestParticipant.contest_id == active_contest.id
                )
            )
        )
        participant = participant_result.scalar_one_or_none()
        
        # Konkurs haqida ma'lumot
        days_left = (active_contest.end_date - datetime.utcnow()).days
        hours_left = (active_contest.end_date - datetime.utcnow()).seconds // 3600
        
        if participant:
            if participant.contest_number:
                # Raqam olgan ishtirokchi
                contest_text = f"""
🏆 <b>REFERAL KONKURS</b> 🏆

✅ Siz konkursda ishtirok qilyapsiz!
🎯 Sizning raqamingiz: <b>{participant.contest_number}</b>

📊 <b>Statistika:</b>
👥 To'plangan referallar: <b>{participant.referrals_completed}/5</b>
📅 Konkurs tugashiga: <b>{days_left} kun {hours_left} soat</b>

🏆 <b>Mukofotlar:</b>
🥇 1-o'rin: 1 oylik Premium
🥈 2-o'rin: 100 yulduz
🥉 3-o'rin: 50 yulduz  
🎖️ 4-5 o'rin: 15 tadan yulduz

🤞 Omad tilaymiz!
                """
                
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="📊 Mening statistikam", callback_data="contest_stats")],
                        [InlineKeyboardButton(text="🔗 Referal link", callback_data="get_referral_link")],
                        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")]
                    ]
                )
            else:
                # Raqam olmagan ishtirokchi
                contest_text = f"""
🏆 <b>REFERAL KONKURS</b> 🏆

📈 <b>Progress:</b> {participant.referrals_completed}/5 referal

⏰ Raqam olish uchun yana <b>{5 - participant.referrals_completed}</b> ta referal kerak!

💡 <b>Eslatma:</b> Referal yulduz sotib olishi va o'ynashi kerak.

📅 Konkurs tugashiga: <b>{days_left} kun {hours_left} soat</b>

🏆 <b>Mukofotlar:</b>
🥇 1-o'rin: 1 oylik Premium
🥈 2-o'rin: 100 yulduz  
🥉 3-o'rin: 50 yulduz
🎖️ 4-5 o'rin: 15 tadan yulduz
                """
                
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="🔗 Referal link olish", callback_data="get_referral_link")],
                        [InlineKeyboardButton(text="📊 Mening statistikam", callback_data="contest_stats")],
                        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")]
                    ]
                )
        else:
            # Konkursda ishtirok etmagan
            contest_text = f"""
🏆 <b>REFERAL KONKURS</b> 🏆

🎯 <b>Vazifa:</b> 5 ta do'stingizni taklif qiling!

📋 <b>Shartlar:</b>
• Har bir referal yulduz sotib olishi kerak
• Referal o'ynashi kerak
• 5 ta referal to'plab raqam oling (1-1000)

📅 Konkurs: <b>{days_left} kun {hours_left} soat</b>

🏆 <b>Mukofotlar:</b>
🥇 1-o'rin: 1 oylik Premium
🥈 2-o'rin: 100 yulduz
🥉 3-o'rin: 50 yulduz
🎖️ 4-5 o'rin: 15 tadan yulduz

🚀 Konkursda ishtirok etasizmi?
            """
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Konkursda ishtirok etish", callback_data="join_contest")],
                    [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")]
                ]
            )
        
        await message.answer(contest_text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data == "join_contest")
async def join_contest(callback: CallbackQuery):
    """Konkursga ro'yxatdan o'tish"""
    async for db in get_db():
        # Faol konkursni topish
        contest_result = await db.execute(
            select(Contest).where(
                Contest.is_active == True,
                Contest.end_date > datetime.utcnow()
            )
        )
        active_contest = contest_result.scalar_one_or_none()
        
        if not active_contest:
            await callback.answer("❌ Faol konkurs topilmadi!", show_alert=True)
            return
        
        # Avval ro'yxatdan o'tganligini tekshirish
        participant_result = await db.execute(
            select(ContestParticipant).where(
                and_(
                    ContestParticipant.user_id == callback.from_user.id,
                    ContestParticipant.contest_id == active_contest.id
                )
            )
        )
        existing_participant = participant_result.scalar_one_or_none()
        
        if existing_participant:
            await callback.answer("✅ Siz allaqachon konkursda ishtirok qilyapsiz!", show_alert=True)
            return
        
        # Konkursga ro'yxatdan o'tkazish
        new_participant = ContestParticipant(
            user_id=callback.from_user.id,
            contest_id=active_contest.id,
            referrals_completed=0
        )
        
        db.add(new_participant)
        await db.commit()
        
        # Referal link berish
        bot_me = await callback.bot.get_me()
        referral_link = f"https://t.me/{bot_me.username}?start=ref_{callback.from_user.id}"
        
        success_text = f"""
✅ <b>Konkursga muvaffaqiyatli ro'yxatdan o'tdingiz!</b>

🔗 <b>Sizning referal linkingiz:</b>
<code>{referral_link}</code>

📋 <b>Vazifa:</b>
• Do'stlaringizga linkni yuboring
• Ular yulduz sotib olishi va o'ynashi kerak  
• 5 ta referal to'plab tasodifiy raqam oling!

🏆 Omad yor bo'lsin!
        """
        
        await callback.message.edit_text(success_text, parse_mode="HTML")
        await callback.answer("🎉 Konkursga qo'shildingiz!")

@router.callback_query(F.data == "contest_stats")
async def contest_statistics(callback: CallbackQuery):
    """Foydalanuvchining konkurs statistikasi"""
    async for db in get_db():
        # Faol konkurs va ishtirokchi ma'lumotlari
        contest_result = await db.execute(
            select(Contest).where(
                Contest.is_active == True,
                Contest.end_date > datetime.utcnow()
            )
        )
        active_contest = contest_result.scalar_one_or_none()
        
        if not active_contest:
            await callback.answer("❌ Faol konkurs yo'q!", show_alert=True)
            return
        
        participant_result = await db.execute(
            select(ContestParticipant).where(
                and_(
                    ContestParticipant.user_id == callback.from_user.id,
                    ContestParticipant.contest_id == active_contest.id
                )
            )
        )
        participant = participant_result.scalar_one_or_none()
        
        if not participant:
            await callback.answer("❌ Siz konkursda ishtirok etmayapsiz!", show_alert=True)
            return
        
        # Umumiy ishtirokchilar soni
        total_participants = await db.scalar(
            select(func.count(ContestParticipant.id)).where(
                ContestParticipant.contest_id == active_contest.id
            )
        )
        
        # Raqam olganlar soni
        qualified_participants = await db.scalar(
            select(func.count(ContestParticipant.id)).where(
                and_(
                    ContestParticipant.contest_id == active_contest.id,
                    ContestParticipant.contest_number.isnot(None)
                )
            )
        )
        
        days_left = (active_contest.end_date - datetime.utcnow()).days
        hours_left = (active_contest.end_date - datetime.utcnow()).seconds // 3600
        
        # Raqam matnini tayyorlash
        number_text = f"#{participant.contest_number}" if participant.contest_number else "Hali yo'q"
        result_text = "🎉 Siz raqam oldingiz! Omad tilaymiz!" if participant.contest_number else "💪 Yana harakat qiling!"
        
        stats_text = f"""
📊 <b>KONKURS STATISTIKASI</b>

👤 <b>Sizning natijangiz:</b>
👥 Referallar: <b>{participant.referrals_completed}/5</b>
🎯 Raqamingiz: <b>{number_text}</b>

📈 <b>Umumiy ma'lumot:</b>
🏆 Jami ishtirokchilar: <b>{total_participants}</b>
🎲 Raqam olganlar: <b>{qualified_participants}</b>
⏰ Qolgan vaqt: <b>{days_left} kun {hours_left} soat</b>

{result_text}
        """
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔗 Referal link", callback_data="get_referral_link")],
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_contest")]
            ]
        )
        
        await callback.message.edit_text(stats_text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data == "back_contest")  
async def back_to_contest(callback: CallbackQuery):
    """Konkurs menyusiga qaytish"""
    # contest_menu funksiyasini chaqirish
    await contest_menu(callback.message)
    await callback.answer()

async def check_and_assign_number(user_id: int, db: AsyncSession):
    """5 ta referal to'planganda raqam berish"""
    # Faol konkursni topish
    contest_result = await db.execute(
        select(Contest).where(
            Contest.is_active == True,
            Contest.end_date > datetime.utcnow()
        )
    )
    active_contest = contest_result.scalar_one_or_none()
    
    if not active_contest:
        return False
    
    # Ishtirokchini topish
    participant_result = await db.execute(
        select(ContestParticipant).where(
            and_(
                ContestParticipant.user_id == user_id,
                ContestParticipant.contest_id == active_contest.id
            )
        )
    )
    participant = participant_result.scalar_one_or_none()
    
    if not participant or participant.contest_number:
        return False
    
    # 5 ta referal to'pladimi tekshirish
    if participant.referrals_completed >= 5:
        # Bo'sh raqam topish
        available_number_result = await db.execute(
            select(ContestNumber).where(
                and_(
                    ContestNumber.contest_id == active_contest.id,
                    ContestNumber.user_id.is_(None)
                )
            ).limit(1000)
        )
        available_numbers = available_number_result.scalars().all()
        
        if available_numbers:
            # Tasodifiy raqam tanlash
            chosen_number = random.choice(available_numbers)
            
            # Raqamni tayinlash
            chosen_number.user_id = user_id
            chosen_number.assigned_at = datetime.utcnow()
            
            # Ishtirokchiga raqamni berish
            participant.contest_number = chosen_number.number_value
            participant.number_assigned_at = datetime.utcnow()
            participant.is_qualified = True
            
            await db.commit()
            return chosen_number.number_value
    
    return False

async def increment_contest_referral(referrer_id: int, db: AsyncSession):
    """Konkurs uchun referal hisobini oshirish"""
    # Faol konkursni topish
    contest_result = await db.execute(
        select(Contest).where(
            Contest.is_active == True,
            Contest.end_date > datetime.utcnow()
        )
    )
    active_contest = contest_result.scalar_one_or_none()
    
    if not active_contest:
        return
    
    # Ishtirokchini topish
    participant_result = await db.execute(
        select(ContestParticipant).where(
            and_(
                ContestParticipant.user_id == referrer_id,
                ContestParticipant.contest_id == active_contest.id
            )
        )
    )
    participant = participant_result.scalar_one_or_none()
    
    if participant and not participant.contest_number:
        participant.referrals_completed += 1
        await db.commit()
        
        # 5 ta to'plansa raqam berish
        if participant.referrals_completed >= 5:
            contest_number = await check_and_assign_number(referrer_id, db)
            return contest_number
    
    return None

@router.message(F.text.startswith("/announce_winners"))
async def announce_winners_command(message: Message):
    """G'oliblarni e'lon qilish komandasi (faqat adminlar uchun)"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Sizda bu komandani ishlatish huquqi yo'q!")
        return
    
    try:
        # Komanda formatini tekshirish: /announce_winners 123 456 789
        parts = message.text.split()
        if len(parts) != 4:
            await message.answer(
                "❌ Noto'g'ri format!\n\n"
                "To'g'ri format:\n"
                "/announce_winners [1-o'rin_raqam] [2-o'rin_raqam] [3-o'rin_raqam]\n\n"
                "Misol: /announce_winners 123 456 789"
            )
            return
        
        winner_1_number = int(parts[1])
        winner_2_number = int(parts[2])
        winner_3_number = int(parts[3])
        
        async for db in get_db():
            # Faol konkursni topish
            contest_result = await db.execute(
                select(Contest).where(
                    Contest.is_active == True,
                    Contest.end_date > datetime.utcnow()
                )
            )
            active_contest = contest_result.scalar_one_or_none()
            
            if not active_contest:
                await message.answer("❌ Faol konkurs topilmadi!")
                return
            
            # G'oliblarni topish
            winners_result = await db.execute(
                select(ContestParticipant, User)
                .join(User, ContestParticipant.user_id == User.telegram_id)
                .where(
                    ContestParticipant.contest_id == active_contest.id,
                    ContestParticipant.contest_number.in_([winner_1_number, winner_2_number, winner_3_number])
                )
            )
            winners = winners_result.all()
            
            if len(winners) != 3:
                await message.answer("❌ Ba'zi g'oliblar topilmadi! Raqamlarni tekshiring.")
                return
            
            # G'oliblarni tartiblash
            winner_1 = None
            winner_2 = None
            winner_3 = None
            
            for participant, user in winners:
                if participant.contest_number == winner_1_number:
                    winner_1 = (participant, user)
                elif participant.contest_number == winner_2_number:
                    winner_2 = (participant, user)
                elif participant.contest_number == winner_3_number:
                    winner_3 = (participant, user)
            
            # Konkursni tugatish
            active_contest.winner_1 = winner_1[1].telegram_id if winner_1 else None
            active_contest.winner_2 = winner_2[1].telegram_id if winner_2 else None
            active_contest.winner_3 = winner_3[1].telegram_id if winner_3 else None
            active_contest.winners_announced = True
            active_contest.is_active = False
            
            await db.commit()
            
            # G'oliblarni e'lon qilish xabari
            winner_1_name = winner_1[1].first_name if winner_1 else 'N/A'
            winner_2_name = winner_2[1].first_name if winner_2 else 'N/A'
            winner_3_name = winner_3[1].first_name if winner_3 else 'N/A'
            
            winner_announcement = f"""
🏆 <b>KONKURS G'OLIBLARI E'LON QILINADI!</b> 🏆

🥇 <b>1-o'rin:</b> {winner_1_name} - #{winner_1_number}
🎁 Mukofot: 1 oylik Premium

🥈 <b>2-o'rin:</b> {winner_2_name} - #{winner_2_number}
🎁 Mukofot: 100 yulduz

🥉 <b>3-o'rin:</b> {winner_3_name} - #{winner_3_number}
🎁 Mukofot: 50 yulduz

🎊 Tabriklaymiz! Mukofotlar admin tomonidan beriladi.
            """
            
            # Barcha ishtirokchilarga e'lon yuborish
            all_participants_result = await db.execute(
                select(ContestParticipant)
                .where(ContestParticipant.contest_id == active_contest.id)
            )
            all_participants = all_participants_result.scalars().all()
            
            sent_count = 0
            for participant in all_participants:
                try:
                    await message.bot.send_message(
                        chat_id=participant.user_id,
                        text=winner_announcement,
                        parse_mode="HTML"
                    )
                    sent_count += 1
                except:
                    pass
            
            # Adminga natija
            admin_result = f"""
✅ <b>G'OLIBLAR E'LON QILINDI!</b>

🏆 G'oliblar:
🥇 {winner_1[1].first_name} (#{winner_1_number})
🥈 {winner_2[1].first_name} (#{winner_2_number})  
🥉 {winner_3[1].first_name} (#{winner_3_number})

📊 Xabar yuborildi: {sent_count} ta ishtirokchiga

💡 Endi mukofotlarni qo'lda bering!
            """
            
            await message.answer(admin_result, parse_mode="HTML")
            
    except ValueError:
        await message.answer("❌ Raqamlar noto'g'ri kiritilgan!")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")
        print(f"Announce winners error: {e}")