from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import uvicorn
import asyncio

from database import get_db
from models import User, Transaction, Withdrawal, SpinResult, Contest, ContestParticipant, ContestNumber
from utils import format_number
from config import ADMIN_IDS

app = FastAPI(title="Telegram Bot Admin Panel")

# Templates va static fayllar
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "message": "Bot Stars application is running"}

@app.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    """Admin panel asosiy sahifa"""
    try:
        # Asosiy statistika
        total_users = await db.scalar(select(func.count(User.id))) or 0
        total_deposits = await db.scalar(select(func.sum(User.total_deposited))) or 0
        total_withdrawals = await db.scalar(select(func.sum(User.total_withdrawn))) or 0
        total_stars_balance = await db.scalar(select(func.sum(User.stars))) or 0
        
        # Bugungi statistika
        today = datetime.now().date()
        today_users = await db.scalar(
            select(func.count(User.id)).where(func.date(User.created_at) == today)
        ) or 0
        
        today_deposits_result = await db.execute(
            select(func.sum(Transaction.amount)).where(
                Transaction.transaction_type == "purchase",
                func.date(Transaction.created_at) == today
            )
        )
        today_deposits = today_deposits_result.scalar() or 0
        
        today_spins = await db.scalar(
            select(func.count(SpinResult.id)).where(func.date(SpinResult.created_at) == today)
        ) or 0
        
        # Kutilayotgan chiqishlar
        pending_withdrawals = await db.scalar(
            select(func.count(Withdrawal.id)).where(Withdrawal.status == "pending")
        ) or 0
        
        # Eng faol foydalanuvchilar
        top_users_result = await db.execute(
            select(User).order_by(desc(User.total_deposited)).limit(10)
        )
        top_users = top_users_result.scalars().all()
        
        # So'nggi tranzaksiyalar
        recent_transactions_result = await db.execute(
            select(Transaction)
            .order_by(desc(Transaction.created_at))
            .limit(20)
        )
        recent_transactions = recent_transactions_result.scalars().all()
        
        return templates.TemplateResponse("admin.html", {
            "request": request,
            "total_users": total_users,
            "total_deposits": format_number(total_deposits),
            "total_withdrawals": format_number(total_withdrawals),
            "total_stars_balance": format_number(total_stars_balance),
            "today_users": today_users,
            "today_deposits": format_number(today_deposits),
            "today_spins": today_spins,
            "pending_withdrawals": pending_withdrawals,
            "profit": format_number(total_deposits - total_withdrawals),
            "top_users": top_users,
            "recent_transactions": recent_transactions,
            "format_number": format_number
        })
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Server error")

@app.get("/withdrawals", response_class=HTMLResponse)
async def withdrawals_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Chiqarish so'rovlari sahifasi"""
    try:
        # Barcha chiqish so'rovlari
        withdrawals_result = await db.execute(
            select(Withdrawal)
            .order_by(desc(Withdrawal.requested_at))
            .limit(100)
        )
        withdrawals = withdrawals_result.scalars().all()
        
        # Har bir chiqish uchun foydalanuvchi ma'lumotlarini olish
        withdrawal_data = []
        for withdrawal in withdrawals:
            user_result = await db.execute(
                select(User).where(User.telegram_id == withdrawal.user_id)
            )
            user = user_result.scalar_one_or_none()
            
            withdrawal_data.append({
                "withdrawal": withdrawal,
                "user": user
            })
        
        return templates.TemplateResponse("admin.html", {
            "request": request,
            "page": "withdrawals",
            "withdrawal_data": withdrawal_data,
            "format_number": format_number
        })
        
    except Exception as e:
        print(f"Withdrawals page error: {e}")
        raise HTTPException(status_code=500, detail="Server error")

@app.post("/approve_withdrawal/{withdrawal_id}")
async def approve_withdrawal_api(withdrawal_id: int, db: AsyncSession = Depends(get_db)):
    """Chiqishni tasdiqlash API"""
    try:
        # Chiqish so'rovini topish
        withdrawal_result = await db.execute(
            select(Withdrawal).where(Withdrawal.id == withdrawal_id)
        )
        withdrawal = withdrawal_result.scalar_one_or_none()
        
        if not withdrawal or withdrawal.status != "pending":
            raise HTTPException(status_code=404, detail="Withdrawal not found or already processed")
        
        # Foydalanuvchini topish
        user_result = await db.execute(
            select(User).where(User.telegram_id == withdrawal.user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Chiqishni tasdiqlash
        withdrawal.status = "approved"
        withdrawal.processed_at = datetime.utcnow()
        
        # Statistikani yangilash
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
        
        return {"status": "success", "message": "Withdrawal approved"}
        
    except Exception as e:
        print(f"Approve withdrawal error: {e}")
        raise HTTPException(status_code=500, detail="Server error")

@app.post("/reject_withdrawal/{withdrawal_id}")
async def reject_withdrawal_api(withdrawal_id: int, db: AsyncSession = Depends(get_db)):
    """Chiqishni rad etish API"""
    try:
        # Chiqish so'rovini topish
        withdrawal_result = await db.execute(
            select(Withdrawal).where(Withdrawal.id == withdrawal_id)
        )
        withdrawal = withdrawal_result.scalar_one_or_none()
        
        if not withdrawal or withdrawal.status != "pending":
            raise HTTPException(status_code=404, detail="Withdrawal not found or already processed")
        
        # Foydalanuvchini topish
        user_result = await db.execute(
            select(User).where(User.telegram_id == withdrawal.user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Chiqishni rad etish
        withdrawal.status = "rejected"
        withdrawal.processed_at = datetime.utcnow()
        withdrawal.admin_note = "Web admin orqali rad etildi"
        
        # Yulduzlarni qaytarish
        user.stars += withdrawal.amount
        
        await db.commit()
        
        return {"status": "success", "message": "Withdrawal rejected"}
        
    except Exception as e:
        print(f"Reject withdrawal error: {e}")
        raise HTTPException(status_code=500, detail="Server error")

@app.get("/users", response_class=HTMLResponse)
async def users_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Foydalanuvchilar sahifasi"""
    try:
        # Barcha foydalanuvchilar
        users_result = await db.execute(
            select(User)
            .order_by(desc(User.total_deposited))
            .limit(100)
        )
        users = users_result.scalars().all()
        
        return templates.TemplateResponse("admin.html", {
            "request": request,
            "page": "users",
            "users": users,
            "format_number": format_number
        })
        
    except Exception as e:
        print(f"Users page error: {e}")
        raise HTTPException(status_code=500, detail="Server error")

@app.get("/contest", response_class=HTMLResponse)
async def contest_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Konkurs sahifasi"""
    try:
        # Faol konkursni topish
        contest_result = await db.execute(
            select(Contest).where(
                Contest.is_active == True,
                Contest.end_date > datetime.utcnow()
            )
        )
        active_contest = contest_result.scalar_one_or_none()
        
        if not active_contest:
            return templates.TemplateResponse("admin.html", {
                "request": request,
                "page": "contest",
                "active_contest": None,
                "participants": [],
                "qualified_participants": [],
                "format_number": format_number
            })
        
        # Barcha ishtirokchilar
        participants_result = await db.execute(
            select(ContestParticipant, User)
            .join(User, ContestParticipant.user_id == User.telegram_id)
            .where(ContestParticipant.contest_id == active_contest.id)
            .order_by(desc(ContestParticipant.referrals_completed))
        )
        participants = participants_result.all()
        
        # Raqam olgan ishtirokchilar
        qualified_result = await db.execute(
            select(ContestParticipant, User)
            .join(User, ContestParticipant.user_id == User.telegram_id)
            .where(
                ContestParticipant.contest_id == active_contest.id,
                ContestParticipant.contest_number.isnot(None)
            )
            .order_by(ContestParticipant.contest_number)
        )
        qualified_participants = qualified_result.all()
        
        # Konkurs statistikasi
        total_participants = len(participants)
        qualified_count = len(qualified_participants)
        
        # Vaqt hisoblash
        time_left = active_contest.end_date - datetime.utcnow()
        days_left = time_left.days
        hours_left = time_left.seconds // 3600
        
        return templates.TemplateResponse("admin.html", {
            "request": request,
            "page": "contest",
            "active_contest": active_contest,
            "participants": participants,
            "qualified_participants": qualified_participants,
            "total_participants": total_participants,
            "qualified_count": qualified_count,
            "days_left": days_left,
            "hours_left": hours_left,
            "format_number": format_number
        })
        
    except Exception as e:
        print(f"Contest page error: {e}")
        raise HTTPException(status_code=500, detail="Server error")

@app.post("/contest/announce_winners")
async def announce_winners_api(request: Request, db: AsyncSession = Depends(get_db)):
    """G'oliblarni e'lon qilish API"""
    try:
        form = await request.form()
        winner_1 = int(form.get("winner_1")) if form.get("winner_1") else None
        winner_2 = int(form.get("winner_2")) if form.get("winner_2") else None  
        winner_3 = int(form.get("winner_3")) if form.get("winner_3") else None
        
        # Faol konkursni topish
        contest_result = await db.execute(
            select(Contest).where(
                Contest.is_active == True,
                Contest.end_date > datetime.utcnow()
            )
        )
        active_contest = contest_result.scalar_one_or_none()
        
        if not active_contest:
            return {"status": "error", "message": "Faol konkurs topilmadi"}
        
        # G'oliblarni saqlash
        active_contest.winner_1 = winner_1
        active_contest.winner_2 = winner_2  
        active_contest.winner_3 = winner_3
        active_contest.winners_announced = True
        active_contest.is_active = False
        
        await db.commit()
        
        return {"status": "success", "message": "G'oliblar e'lon qilindi!"}
        
    except Exception as e:
        print(f"Announce winners error: {e}")
        return {"status": "error", "message": "Server xatolik"}

@app.get("/messages", response_class=HTMLResponse)
async def messages_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Xabarlar sahifasi"""
    try:
        # Jami foydalanuvchilar soni
        total_users = await db.scalar(select(func.count(User.id))) or 0
        
        return templates.TemplateResponse("admin.html", {
            "request": request,
            "page": "messages",
            "total_users": total_users,
            "format_number": format_number
        })
        
    except Exception as e:
        print(f"Messages page error: {e}")
        raise HTTPException(status_code=500, detail="Server error")

@app.post("/send_message_to_all")
async def send_message_to_all_api(
    request: Request,
    title: str = Form(...),
    text: str = Form(...),
    type: str = Form(...),
    active_only: bool = Form(False),
    db: AsyncSession = Depends(get_db)
):
    """Barcha foydalanuvchilarga xabar yuborish API"""
    try:
        start_time = datetime.now()
        
        # Foydalanuvchilarni olish
        if active_only:
            # Faqat faol foydalanuvchilar (son 7 kunda yaratilgan yoki tranzaksiya qilgan)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            users_result = await db.execute(
                select(User).where(
                    (User.created_at >= seven_days_ago) |
                    (User.telegram_id.in_(
                        select(Transaction.user_id).where(Transaction.created_at >= seven_days_ago)
                    ))
                )
            )
        else:
            # Barcha foydalanuvchilar
            users_result = await db.execute(select(User))
        
        users = users_result.scalars().all()
        
        if not users:
            return JSONResponse({
                "status": "error",
                "message": "Yuborish uchun foydalanuvchilar topilmadi"
            })
        
        # Xabar matnini tayyorlash
        message_type_emoji = {
            "announcement": "📢",
            "update": "🔄", 
            "promotion": "🎁",
            "maintenance": "🔧",
            "other": "📝"
        }
        
        emoji = message_type_emoji.get(type, "📝")
        full_message = f"""
{emoji} <b>{title}</b> {emoji}

{text}

📅 <i>Yuborilgan vaqt: {datetime.now().strftime('%d.%m.%Y %H:%M')}</i>
        """
        
        # Bot instance yaratish (bot.py dan import qilish)
        from bot import bot
        
        sent_count = 0
        error_count = 0
        
        # Har bir foydalanuvchiga xabar yuborish
        for user in users:
            try:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=full_message,
                    parse_mode="HTML"
                )
                sent_count += 1
                
                # Rate limiting - har 50 xabardan keyin 1 soniya kutish
                if sent_count % 50 == 0:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                print(f"Xabar yuborishda xatolik (user {user.telegram_id}): {e}")
                error_count += 1
                continue
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return JSONResponse({
            "status": "success",
            "message": "Xabar muvaffaqiyatli yuborildi",
            "sent_count": sent_count,
            "error_count": error_count,
            "total_users": len(users),
            "duration": round(duration, 2)
        })
        
    except Exception as e:
        print(f"Send message to all error: {e}")
        return JSONResponse({
            "status": "error",
            "message": f"Server xatolik: {str(e)}"
        })

if __name__ == "__main__":
    import os
    uvicorn.run(
        "admin_panel:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=False
    )
