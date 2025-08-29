from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User, Transaction
from keyboards import get_star_purchase_keyboard
from config import STAR_PACKAGES, PAYMENT_PROVIDER_TOKEN
from utils import format_number, generate_transaction_id

router = Router()

@router.message(F.text == "⭐ Yulduz sotib olish")
async def buy_stars_menu(message: Message):
    """Yulduz sotib olish menyusi"""
    text = """
⭐ <b>YULDUZ SOTIB OLISH</b>

Quyidagi paketlardan birini tanlang:

💰 <b>Mavjud paketlar:</b>
"""
    
    for stars, price in STAR_PACKAGES.items():
        text += f"• {stars} ⭐ = {price} Telegram Stars\n"
    
    text += """
💡 <b>Eslatma:</b>
• To'lov Telegram Stars orqali amalga oshiriladi
• Yulduzlar darhol hisobingizga qo'shiladi
• Xavfsiz va tezkor to'lov tizimi
    """
    
    await message.answer(
        text,
        reply_markup=get_star_purchase_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("buy_stars_"))
async def process_star_purchase(callback: CallbackQuery):
    """Yulduz sotib olish jarayoni"""
    try:
        stars_amount = int(callback.data.split("_")[2])
        price = STAR_PACKAGES.get(stars_amount)
        
        if not price:
            await callback.answer("❌ Noto'g'ri paket tanlandi", show_alert=True)
            return
        
        # Invoice yaratish
        await callback.bot.send_invoice(
            chat_id=callback.from_user.id,
            title=f"⭐ {stars_amount} Yulduz",
            description=f"{stars_amount} yulduz sotib olish",
            payload=f"stars_{stars_amount}_{generate_transaction_id()}",
            provider_token=PAYMENT_PROVIDER_TOKEN,
            currency="XTR",  # Telegram Stars currency
            prices=[LabeledPrice(label=f"{stars_amount} Yulduz", amount=price)],
            start_parameter="star_purchase"
        )
        
        await callback.answer("💳 To'lov oynasi yuborildi")
        
    except Exception as e:
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        print(f"Payment error: {e}")

@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    """To'lovni tasdiqlash"""
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    """Muvaffaqiyatli to'lov"""
    try:
        payment = message.successful_payment
        payload_parts = payment.invoice_payload.split("_")
        
        if len(payload_parts) < 3 or payload_parts[0] != "stars":
            await message.answer("❌ To'lov ma'lumotlarida xatolik")
            return
        
        stars_amount = int(payload_parts[1])
        transaction_id = payload_parts[2]
        
        async for db in get_db():
            # Foydalanuvchini topish
            result = await db.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await message.answer("❌ Foydalanuvchi topilmadi")
                return
            
            # Balansni yangilash
            user.stars += stars_amount
            user.total_deposited += stars_amount
            
            # Tranzaksiyani saqlash
            transaction = Transaction(
                user_id=user.telegram_id,
                transaction_type="purchase",
                amount=stars_amount,
                description=f"Yulduz sotib olish: {stars_amount} ⭐",
                telegram_payment_id=payment.telegram_payment_charge_id
            )
            
            db.add(transaction)
            await db.commit()
            
            success_text = f"""
✅ <b>TO'LOV MUVAFFAQIYATLI!</b>

🎉 Sizning hisobingizga <b>{format_number(stars_amount)} ⭐</b> qo'shildi!

💰 <b>To'lov ma'lumotlari:</b>
🆔 Tranzaksiya ID: {transaction_id}
💳 To'lov miqdori: {payment.total_amount} XTR
📅 Sana: {message.date.strftime('%d.%m.%Y %H:%M')}

⭐ <b>Yangi balans:</b> {format_number(user.stars)} yulduz

Endi o'yin o'ynashingiz mumkin! 🎰
            """
            
            await message.answer(success_text, parse_mode="HTML")
            
    except Exception as e:
        await message.answer("❌ To'lov qayta ishlanishida xatolik yuz berdi")
        print(f"Payment processing error: {e}")
