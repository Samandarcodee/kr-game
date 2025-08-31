import asyncio
import uvicorn
import os
from bot import main as bot_main
from admin_panel import app

async def run_bot():
    """Bot ishga tushirish"""
    await bot_main()

async def run_admin_panel():
    """Admin panel ishga tushirish"""
    config = uvicorn.Config(
        "admin_panel:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=False
    )
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    """Asosiy funktsiya - bot va admin panelni parallel ishga tushirish"""
    try:
        print("🚀 Bot va Admin panel ishga tushirilmoqda...")
        
        # Bot va admin panelni parallel ishga tushirish
        await asyncio.gather(
            run_bot(),
            run_admin_panel()
        )
        
    except Exception as e:
        print(f"❌ Xatolik yuz berdi: {e}")

if __name__ == "__main__":
    asyncio.run(main())
