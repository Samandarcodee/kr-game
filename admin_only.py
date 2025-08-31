#!/usr/bin/env python3
"""
Admin panel only mode for BotStars
This can run without the bot for testing the admin panel
"""

import os
import uvicorn
from admin_panel import app

def main():
    """Start admin panel only"""
    print("🚀 Starting BotStars Admin Panel Only...")
    print("=" * 50)
    
    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        print("❌ DATABASE_URL environment variable is not set!")
        print("Please set DATABASE_URL in Railway environment variables")
        return
    
    print("✅ Database URL is set")
    print("Starting admin panel...")
    
    # Start the admin panel
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "admin_panel:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )

if __name__ == "__main__":
    main()
