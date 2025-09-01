# 🚀 Vercel Deployment Guide

## Vercel Server Error muammosini hal qilish

### 1. Vercel ga o'ting
[Vercel.com](https://vercel.com) → GitHub bilan login

### 2. Yangi loyiha yarating
- "New Project" bosing
- GitHub repository ni import qiling: `Samandarcodee/kr-game`
- "Deploy" bosing

### 3. Environment Variables qo'shing
Vercel dashboard da "Settings" → "Environment Variables" ga o'ting va quyidagilarni qo'shing:

```bash
# Database (Neon.tech dan)
DATABASE_URL=postgresql://neondb_owner:npg_kPUu0csMVL6t@ep-snowy-dawn-adfbba3b.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require

# Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_IDS=your_telegram_id

# Optional
PAYMENT_PROVIDER_TOKEN=your_payment_token
```

### 4. Redeploy
- "Deployments" ga o'ting
- "Redeploy" bosing

## Server Error muammolari

### Muammo 1: "Server error" xatosi
**Yechim:**
- Environment variables to'g'ri o'rnatilganini tekshiring
- DATABASE_URL ni to'g'ri ko'chirib qo'yganingizni tekshiring
- Redeploy qiling

### Muammo 2: Build failed
**Yechim:**
- requirements.txt da barcha paketlar borligini tekshiring
- Python versiyasi 3.11 ekanligini tekshiring

### Muammo 3: Database connection error
**Yechim:**
- DATABASE_URL ni to'g'ri ko'chirib qo'yganingizni tekshiring
- Neon.tech database ishlayotganini tekshiring

## Health Check

Deployment muvaffaqiyatli bo'lganini tekshiring:
```
https://your-app.vercel.app/
```

Response:
```json
{
  "status": "healthy",
  "message": "BotStars API is running on Vercel",
  "database_url_set": true,
  "bot_token_set": true,
  "admin_ids_set": true
}
```

## Logs ko'rish

Vercel dashboard da:
1. Project → "Functions" ga o'ting
2. "View Function Logs" bosing
3. Xatolarni ko'ring

## Bot Token olish

1. [@BotFather](https://t.me/BotFather) ga o'ting
2. `/newbot` buyrug'ini yuboring
3. Bot nomi va username bering
4. Token ni oling

## Admin ID olish

1. [@userinfobot](https://t.me/userinfobot) ga o'ting
2. ID ni oling

## Support

Muammolar bo'lsa:
- Vercel logs ni tekshiring
- Environment variables ni qayta tekshiring
- Database connection ni tekshiring
