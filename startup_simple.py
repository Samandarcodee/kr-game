#!/usr/bin/env python3
"""
Simple startup script for BotStars application
Starts admin panel first to ensure health checks work
"""

import os
import sys
import uvicorn
from admin_panel import app

def main():
    """Start admin panel with health check"""
    print("🚀 Starting BotStars Admin Panel...")
    print("=" * 50)
    
    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        print("❌ DATABASE_URL environment variable is not set!")
        print("Please add PostgreSQL database to your Railway project")
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
