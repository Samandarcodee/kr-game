import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database import init_db
from handlers import start, payments, game, admin
from handlers.withdrawals import router as withdrawal_router
from handlers.support import router as support_router
from handlers.referral import router as referral_router
from handlers.contest import router as contest_router

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot va Dispatcher yaratish
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Routerlarni ro'yxatdan o'tkazish
dp.include_router(start.router)
dp.include_router(payments.router)
dp.include_router(game.router)
dp.include_router(withdrawal_router)
dp.include_router(support_router)
dp.include_router(referral_router)
dp.include_router(contest_router)
dp.include_router(admin.router)

async def main():
    """Asosiy funktsiya"""
    try:
        # Ma'lumotlar bazasini ishga tushirish
        await init_db()
        logger.info("Database initialized successfully")
        
        # Botni ishga tushirish
        logger.info("Starting bot...")
        await dp.start_polling(bot, skip_updates=True)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
