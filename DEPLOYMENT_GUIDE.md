# BotStars Deployment Guide

## Railway Deployment

### 1. Railway ga kirish
- [Railway.app](https://railway.app) ga o'ting
- GitHub bilan login qiling

### 2. Yangi loyiha yaratish
- "New Project" bosing
- "Deploy from GitHub repo" tanlang
- GitHub repository ni tanlang

### 3. PostgreSQL Database qo'shish
- "New" bosing
- "Database" tanlang
- "PostgreSQL" tanlang
- Database yaratilgandan so'ng, Railway avtomatik `DATABASE_URL` ni o'rnatadi

### 4. Environment Variables
Quyidagi environment variables ni qo'shing:

```
BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=your_telegram_id
PAYMENT_PROVIDER_TOKEN=your_payment_token
```

### 5. Deploy
- Railway avtomatik deploy qiladi
- Logs ni tekshiring

## Vercel Deployment

### 1. Vercel ga kirish
- [Vercel.com](https://vercel.com) ga o'ting
- GitHub bilan login qiling

### 2. Yangi loyiha yaratish
- "New Project" bosing
- GitHub repository ni import qiling

### 3. Environment Variables
Vercel dashboard da quyidagi variables ni qo'shing:

```
DATABASE_URL=your_postgresql_connection_string
BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=your_telegram_id
PAYMENT_PROVIDER_TOKEN=your_payment_token
```

### 4. Deploy
- "Deploy" bosing
- Build jarayoni tugagandan so'ng URL olasiz

## Database Setup

### PostgreSQL Database yaratish
1. Railway yoki Vercel da PostgreSQL service qo'shing
2. Database URL ni environment variable ga qo'shing
3. Database avtomatik yaratiladi

### Database Migration
Database jadvallari avtomatik yaratiladi. Agar qo'lda yaratish kerak bo'lsa:

```python
python -c "from database import init_db; import asyncio; asyncio.run(init_db())"
```

## Health Check

Deployment muvaffaqiyatli bo'lganini tekshirish:

- Railway: `https://your-app.railway.app/health`
- Vercel: `https://your-app.vercel.app/health`

## Troubleshooting

### Umumiy muammolar:
1. **DATABASE_URL not set** - PostgreSQL service qo'shing
2. **Build failed** - requirements.txt ni tekshiring
3. **Port issues** - PORT environment variable ni tekshiring

### Logs ko'rish:
- Railway: Project → Deployments → View Logs
- Vercel: Project → Functions → View Logs

## Bot Configuration

### Telegram Bot Token
1. [@BotFather](https://t.me/BotFather) ga o'ting
2. Yangi bot yarating
3. Token ni `BOT_TOKEN` ga qo'shing

### Admin ID
1. [@userinfobot](https://t.me/userinfobot) ga o'ting
2. ID ni oling va `ADMIN_IDS` ga qo'shing

## Monitoring

- Railway: Real-time logs va metrics
- Vercel: Analytics va performance monitoring
- Database: Connection monitoring

## Security

- Environment variables ni hech qachon code ga qo'ymang
- Database URL ni xavfsiz saqlang
- Admin panel ga faqat admin ID lar kirishini ta'minlang
