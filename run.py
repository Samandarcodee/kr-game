import asyncio
import multiprocessing
import uvicorn
from bot import main as bot_main
from admin_panel import app

def run_bot():
    """Bot ishga tushirish"""
    asyncio.run(bot_main())

def run_admin_panel():
    """Admin panel ishga tushirish"""
    uvicorn.run(
        "admin_panel:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )

if __name__ == "__main__":
    # Bot va Admin panelni parallel ishga tushirish
    bot_process = multiprocessing.Process(target=run_bot)
    admin_process = multiprocessing.Process(target=run_admin_panel)
    
    try:
        print("🚀 Bot va Admin panel ishga tushirilmoqda...")
        
        # Jarayonlarni boshlash
        bot_process.start()
        admin_process.start()
        
        print("✅ Bot ishga tushdi!")
        print("✅ Admin panel http://localhost:8000 da ishlamoqda")
        print("📱 Bot foydalanishga tayyor!")
        
        # Jarayonlarni kutish
        bot_process.join()
        admin_process.join()
        
    except KeyboardInterrupt:
        print("\n⏹️ Jarayonlar to'xtatilmoqda...")
        
        # Jarayonlarni to'xtatish
        if bot_process.is_alive():
            bot_process.terminate()
            bot_process.join()
        
        if admin_process.is_alive():
            admin_process.terminate()
            admin_process.join()
        
        print("✅ Barcha jarayonlar to'xtatildi")
    
    except Exception as e:
        print(f"❌ Xatolik yuz berdi: {e}")
        
        # Xatolik holatida jarayonlarni to'xtatish
        if bot_process.is_alive():
            bot_process.terminate()
        if admin_process.is_alive():
            admin_process.terminate()
