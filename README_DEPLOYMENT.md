# 🚀 BotStars - Quick Deployment

## Railway Deployment (Tavsiya etiladi)

### 1. Railway ga o'ting
[Railway.app](https://railway.app) → GitHub bilan login

### 2. Yangi loyiha yarating
- "New Project" → "Deploy from GitHub repo"
- Repository ni tanlang

### 3. PostgreSQL qo'shing
- "New" → "Database" → "PostgreSQL"
- Railway avtomatik `DATABASE_URL` ni o'rnatadi

### 4. Environment Variables
```
BOT_TOKEN=your_bot_token_from_botfather
ADMIN_IDS=your_telegram_id
PAYMENT_PROVIDER_TOKEN=your_payment_token
```

### 5. Deploy
Railway avtomatik deploy qiladi!

## Vercel Deployment

### 1. Vercel ga o'ting
[Vercel.com](https://vercel.com) → GitHub bilan login

### 2. Repository ni import qiling
- "New Project" → GitHub repository ni tanlang

### 3. Environment Variables
```
DATABASE_URL=your_postgresql_url
BOT_TOKEN=your_bot_token
ADMIN_IDS=your_telegram_id
PAYMENT_PROVIDER_TOKEN=your_payment_token
```

### 4. Deploy
"Deploy" bosing!

## Bot Token olish

1. [@BotFather](https://t.me/BotFather) ga o'ting
2. `/newbot` buyrug'ini yuboring
3. Bot nomi va username bering
4. Token ni oling va `BOT_TOKEN` ga qo'shing

## Admin ID olish

1. [@userinfobot](https://t.me/userinfobot) ga o'ting
2. ID ni oling va `ADMIN_IDS` ga qo'shing

## Health Check

Deployment muvaffaqiyatli bo'lganini tekshiring:
- Railway: `https://your-app.railway.app/health`
- Vercel: `https://your-app.vercel.app/health`

## Muammolar?

- **DATABASE_URL not set**: PostgreSQL service qo'shing
- **Build failed**: requirements.txt ni tekshiring
- **Bot ishlamayapti**: BOT_TOKEN ni to'g'ri o'rnatganingizni tekshiring

## Support

Muammolar bo'lsa, logs ni tekshiring:
- Railway: Project → Deployments → View Logs
- Vercel: Project → Functions → View Logs
