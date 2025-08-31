#!/usr/bin/env python3
"""
Startup script for BotStars application
Checks environment variables and starts the application
"""

import os
import sys
import asyncio
from run import main

def check_environment():
    """Check if required environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = {
        'BOT_TOKEN': 'Telegram bot token from @BotFather',
        'ADMIN_IDS': 'Comma-separated admin Telegram IDs',
        'DATABASE_URL': 'PostgreSQL database URL (auto-set by Railway)',
    }
    
    optional_vars = {
        'PAYMENT_PROVIDER_TOKEN': 'Telegram Stars payment provider token'
    }
    
    missing_vars = []
    
    # Check required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value in ['your_bot_token_here', '123456789']:
            print(f"❌ {var}: {description} - NOT SET")
            missing_vars.append(var)
        else:
            print(f"✅ {var}: Set")
    
    # Check optional variables
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if not value or value in ['your_payment_provider_token']:
            print(f"⚠️  {var}: {description} - NOT SET (Optional)")
        else:
            print(f"✅ {var}: Set")
    
    if missing_vars:
        print("\n🚨 Missing required environment variables!")
        print("Please set the following variables in Railway:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nYou can set them in Railway dashboard:")
        print("1. Go to your Railway project")
        print("2. Click on 'Variables' tab")
        print("3. Add the missing environment variables")
        return False
    
    print("✅ All required environment variables are set!")
    return True

def main_startup():
    """Main startup function"""
    print("🚀 Starting BotStars application...")
    print("=" * 50)
    
    # Check environment variables
    if not check_environment():
        print("\n❌ Application cannot start due to missing environment variables")
        print("Please set the required variables and restart the application")
        sys.exit(1)
    
    print("\n✅ Environment check passed!")
    print("Starting application...")
    print("=" * 50)
    
    # Start the application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Application stopped by user")
    except Exception as e:
        print(f"\n❌ Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main_startup()
