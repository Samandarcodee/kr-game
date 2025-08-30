from datetime import datetime
from sqlalchemy import BigInteger, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    stars: Mapped[int] = mapped_column(Integer, default=0)
    total_deposited: Mapped[int] = mapped_column(Integer, default=0)
    total_won: Mapped[int] = mapped_column(Integer, default=0)
    total_withdrawn: Mapped[int] = mapped_column(Integer, default=0)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    captcha_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Referal tizimi
    referrer_id: Mapped[int] = mapped_column(BigInteger, nullable=True)  # Kim taklif qilgan
    total_referrals: Mapped[int] = mapped_column(Integer, default=0)  # Nechta kishi taklif qilgan
    referral_earnings: Mapped[int] = mapped_column(Integer, default=0)  # Referal orqali topgan yulduzlar
    free_spins: Mapped[int] = mapped_column(Integer, default=0)  # Bepul spinlar
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user")
    withdrawals = relationship("Withdrawal", back_populates="user")
    spins = relationship("SpinResult", back_populates="user")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)  # purchase, win, withdrawal
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    telegram_payment_id: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="transactions")

class Withdrawal(Base):
    __tablename__ = "withdrawals"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, approved, rejected
    admin_note: Mapped[str] = mapped_column(Text, nullable=True)
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    processed_by: Mapped[int] = mapped_column(BigInteger, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="withdrawals")

class SpinResult(Base):
    __tablename__ = "spin_results"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    bet_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    win_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    spin_result: Mapped[str] = mapped_column(String(50), nullable=False)  # win, lose
    multiplier: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="spins")

class Contest(Base):
    __tablename__ = "contests"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    start_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    winner_1: Mapped[int] = mapped_column(BigInteger, nullable=True)
    winner_2: Mapped[int] = mapped_column(BigInteger, nullable=True)
    winner_3: Mapped[int] = mapped_column(BigInteger, nullable=True)
    winners_announced: Mapped[bool] = mapped_column(Boolean, default=False)
    
class ContestParticipant(Base):
    __tablename__ = "contest_participants"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    contest_id: Mapped[int] = mapped_column(Integer, ForeignKey("contests.id"), default=1)
    referrals_completed: Mapped[int] = mapped_column(Integer, default=0)
    contest_number: Mapped[int] = mapped_column(Integer, nullable=True)
    number_assigned_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_qualified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    user = relationship("User")
    
class ContestNumber(Base):
    __tablename__ = "contest_numbers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contest_id: Mapped[int] = mapped_column(Integer, ForeignKey("contests.id"), default=1)
    number_value: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")
