import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import DATABASE_URL

class Base(DeclarativeBase):
    pass

# Convert DATABASE_URL to async format if needed
if DATABASE_URL.startswith("postgresql://"):
    async_database_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    async_database_url = DATABASE_URL

# Remove SSL mode parameter if it exists
if "?sslmode=" in async_database_url:
    async_database_url = async_database_url.split("?sslmode=")[0]

engine = create_async_engine(
    async_database_url,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"server_settings": {"application_name": "telegram_bot"}}
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
