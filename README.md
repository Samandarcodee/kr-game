# Telegram Bot Stars - Railway Deployment

A Telegram bot for a star-based gaming platform with an admin panel for managing users, transactions, and withdrawals.

## Features

- 🌟 Star-based gaming system
- 💰 Payment integration with Telegram Stars
- 🎰 Slot-style games with configurable return rates
- 💸 Withdrawal system with admin approval
- 👥 Referral system with bonuses
- 🏆 Contest system
- 📊 Comprehensive admin panel
- 📨 Mass messaging system for admins

## Railway Deployment

### Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Git Repository**: Push your code to GitHub/GitLab
3. **Environment Variables**: Prepare the required environment variables

### Required Environment Variables

Set these environment variables in your Railway project:

```bash
# Bot Configuration
BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=123456789,987654321

# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database

# Payment Configuration
PAYMENT_PROVIDER_TOKEN=your_payment_provider_token

# Webhook Configuration (Optional - Railway will provide the domain)
WEBHOOK_HOST=your-railway-app.railway.app
```

### Deployment Steps

1. **Connect Repository**
   - Go to Railway dashboard
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

2. **Add PostgreSQL Database**
   - In your Railway project, click "New"
   - Select "Database" → "PostgreSQL"
   - Railway will automatically set the `DATABASE_URL` environment variable

3. **Set Environment Variables**
   - Go to your project settings
   - Add all required environment variables listed above

4. **Deploy**
   - Railway will automatically detect the Python project
   - It will install dependencies from `requirements.txt`
   - The app will start using the `Procfile`

### Environment Variables Explained

- **BOT_TOKEN**: Your Telegram bot token from @BotFather
- **ADMIN_IDS**: Comma-separated list of admin Telegram user IDs
- **DATABASE_URL**: PostgreSQL connection string (auto-set by Railway)
- **PAYMENT_PROVIDER_TOKEN**: Telegram Stars payment provider token
- **WEBHOOK_HOST**: Your Railway app domain (optional)

### Database Setup

The application will automatically create all necessary tables on first run. No manual database setup is required.

### Health Check

Railway will automatically check the health of your application at the root path (`/`). The admin panel dashboard serves as the health check endpoint.

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Telegram bot token

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd BotStars
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export BOT_TOKEN=your_bot_token
   export ADMIN_IDS=123456789
   export DATABASE_URL=postgresql://user:password@localhost/dbname
   export PAYMENT_PROVIDER_TOKEN=your_payment_token
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

## Project Structure

```
BotStars/
├── admin_panel.py          # FastAPI admin panel
├── bot.py                  # Main bot file
├── config.py              # Configuration settings
├── database.py            # Database connection
├── models.py              # SQLAlchemy models
├── keyboards.py           # Telegram keyboards
├── handlers/              # Bot handlers
│   ├── start.py          # Start command handler
│   ├── payments.py       # Payment handlers
│   ├── game.py           # Game logic
│   ├── admin.py          # Admin commands
│   ├── withdrawals.py    # Withdrawal handlers
│   ├── support.py        # Support system
│   ├── referral.py       # Referral system
│   └── contest.py        # Contest system
├── templates/             # Admin panel templates
├── static/               # Static files
├── utils.py              # Utility functions
├── utils_captcha.py      # Captcha system
├── utils_subscription.py # Subscription checker
├── run.py                # Application entry point
├── requirements.txt      # Python dependencies
├── Procfile             # Railway deployment
├── railway.json         # Railway configuration
└── README.md            # This file
```

## Admin Panel

The admin panel is available at `https://your-app.railway.app` and provides:

- 📊 Real-time statistics dashboard
- 💰 Withdrawal approval system
- 👥 User management
- 🏆 Contest management
- 📨 Mass messaging system

## Support

For issues and questions:
1. Check the logs in Railway dashboard
2. Verify all environment variables are set correctly
3. Ensure your bot token is valid
4. Check database connectivity

## License

This project is proprietary software.
