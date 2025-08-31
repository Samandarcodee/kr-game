#!/usr/bin/env python3
"""
Test script to verify deployment structure
"""

import os
import sys

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        import asyncio
        print("✅ asyncio imported")
    except ImportError as e:
        print(f"❌ asyncio import failed: {e}")
        return False
    
    try:
        import fastapi
        print("✅ fastapi imported")
    except ImportError as e:
        print(f"❌ fastapi import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ uvicorn imported")
    except ImportError as e:
        print(f"❌ uvicorn import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✅ sqlalchemy imported")
    except ImportError as e:
        print(f"❌ sqlalchemy import failed: {e}")
        return False
    
    try:
        import asyncpg
        print("✅ asyncpg imported")
    except ImportError as e:
        print(f"❌ asyncpg import failed: {e}")
        return False
    
    try:
        import aiogram
        print("✅ aiogram imported")
    except ImportError as e:
        print(f"❌ aiogram import failed: {e}")
        return False
    
    return True

def test_project_structure():
    """Test that all required files exist"""
    print("\nTesting project structure...")
    
    required_files = [
        'requirements.txt',
        'Procfile',
        'railway.json',
        'runtime.txt',
        'README.md',
        'run.py',
        'admin_panel.py',
        'bot.py',
        'config.py',
        'database.py',
        'models.py',
        '.gitignore'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            missing_files.append(file)
    
    return len(missing_files) == 0

def test_admin_panel_structure():
    """Test admin panel structure"""
    print("\nTesting admin panel structure...")
    
    try:
        # Test admin panel import without running
        import admin_panel
        print("✅ admin_panel.py imports successfully")
        
        # Check if app exists
        if hasattr(admin_panel, 'app'):
            print("✅ FastAPI app exists")
        else:
            print("❌ FastAPI app not found")
            return False
            
    except Exception as e:
        print(f"❌ admin_panel.py import failed: {e}")
        return False
    
    return True

def test_templates():
    """Test template files"""
    print("\nTesting templates...")
    
    if os.path.exists('templates'):
        print("✅ templates directory exists")
        
        if os.path.exists('templates/admin.html'):
            print("✅ admin.html template exists")
        else:
            print("❌ admin.html template missing")
            return False
    else:
        print("❌ templates directory missing")
        return False
    
    return True

def test_handlers():
    """Test handler files"""
    print("\nTesting handlers...")
    
    if os.path.exists('handlers'):
        print("✅ handlers directory exists")
        
        handler_files = [
            'handlers/start.py',
            'handlers/payments.py',
            'handlers/game.py',
            'handlers/admin.py',
            'handlers/withdrawals.py',
            'handlers/support.py',
            'handlers/referral.py',
            'handlers/contest.py'
        ]
        
        for handler in handler_files:
            if os.path.exists(handler):
                print(f"✅ {handler} exists")
            else:
                print(f"❌ {handler} missing")
                return False
    else:
        print("❌ handlers directory missing")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Testing BotStars deployment structure...\n")
    
    tests = [
        test_imports,
        test_project_structure,
        test_admin_panel_structure,
        test_templates,
        test_handlers
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Project is ready for Railway deployment.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
