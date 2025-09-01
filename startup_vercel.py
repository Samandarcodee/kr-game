#!/usr/bin/env python3
"""
Vercel deployment uchun startup script
"""

import os
import asyncio
from admin_panel import app
import uvicorn

# Vercel uchun port
PORT = int(os.getenv("PORT", 8000))

if __name__ == "__main__":
    print("🚀 BotStars Vercel deployment starting...")
    print(f"Port: {PORT}")
    
    # Database URL tekshirish
    if not os.getenv("DATABASE_URL"):
        print("⚠️ DATABASE_URL environment variable is not set!")
        print("Please set DATABASE_URL in Vercel environment variables")
    
    # Server ishga tushirish
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
