from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import uvicorn

from database import get_db
from models import User, Transaction, Withdrawal, SpinResult
from utils import format_number

app = FastAPI(title="Telegram Bot Admin Panel")

# Templates va static fayllar
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

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

if __name__ == "__main__":
    uvicorn.run(
        "admin_panel:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
