import os
from typing import Optional

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")
ADMIN_IDS = [int(id_) for id_ in os.getenv("ADMIN_IDS", "123456789").split(",")]

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/telegram_bot")

# Payment configuration
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN", "your_payment_provider_token")

# Star prices (in Telegram Stars)
STAR_PACKAGES = {
    1: 1,
    10: 10,
    25: 25,
    50: 50,
    100: 100,
    200: 200,
    500: 500,
    1000: 1000
}

# Game configuration
MIN_WITHDRAWAL = 150
RETURN_RATE = 0.30  # 30% return rate
SPIN_COST = 10  # Cost per spin in stars

# Webhook configuration
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "your_domain.com")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"https://{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Admin panel configuration
ADMIN_PORT = 8000

# Channel configuration
REQUIRED_CHANNEL = "@premiu_m002"
REQUIRED_CHANNEL_ID = -1002374607763  # Channel ID
