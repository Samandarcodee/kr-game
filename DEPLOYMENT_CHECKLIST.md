# Railway Deployment Checklist

## Pre-Deployment Checklist

### ✅ Code Preparation
- [ ] All files committed to Git repository
- [ ] `requirements.txt` created with all dependencies
- [ ] `Procfile` created for Railway
- [ ] `railway.json` configured
- [ ] `.gitignore` excludes unnecessary files
- [ ] `README.md` contains deployment instructions

### ✅ Environment Variables
- [ ] `BOT_TOKEN` - Telegram bot token from @BotFather
- [ ] `ADMIN_IDS` - Comma-separated admin Telegram IDs
- [ ] `DATABASE_URL` - Will be auto-set by Railway PostgreSQL
- [ ] `PAYMENT_PROVIDER_TOKEN` - Telegram Stars payment token
- [ ] `WEBHOOK_HOST` - Railway app domain (optional)

### ✅ Database Setup
- [ ] PostgreSQL database added to Railway project
- [ ] Database connection tested
- [ ] All tables will be auto-created on first run

### ✅ Application Configuration
- [ ] `run.py` updated for Railway deployment
- [ ] `admin_panel.py` uses PORT environment variable
- [ ] Health check endpoint added (`/health`)
- [ ] Error handling implemented

## Deployment Steps

### 1. Railway Setup
- [ ] Create Railway account
- [ ] Create new project
- [ ] Connect GitHub repository
- [ ] Add PostgreSQL database

### 2. Environment Variables
- [ ] Set `BOT_TOKEN`
- [ ] Set `ADMIN_IDS`
- [ ] Set `PAYMENT_PROVIDER_TOKEN`
- [ ] Verify `DATABASE_URL` is auto-set

### 3. Deploy
- [ ] Push code to GitHub
- [ ] Railway auto-deploys
- [ ] Check build logs
- [ ] Verify health check passes

### 4. Post-Deployment
- [ ] Test bot functionality
- [ ] Test admin panel access
- [ ] Verify database connectivity
- [ ] Check all features work

## Troubleshooting

### Common Issues

1. **Build Fails**
   - Check `requirements.txt` syntax
   - Verify Python version in `runtime.txt`
   - Check for missing dependencies

2. **Bot Not Starting**
   - Verify `BOT_TOKEN` is correct
   - Check bot permissions
   - Review Railway logs

3. **Database Connection Issues**
   - Verify `DATABASE_URL` is set
   - Check PostgreSQL service is running
   - Test connection manually

4. **Admin Panel Not Accessible**
   - Check if app is running on correct port
   - Verify health check endpoint
   - Check Railway domain configuration

### Useful Commands

```bash
# Check Railway logs
railway logs

# Check environment variables
railway variables

# Restart service
railway service restart

# Check service status
railway status
```

## Monitoring

### Health Check
- Endpoint: `https://your-app.railway.app/health`
- Expected response: `{"status": "healthy", "message": "Bot Stars application is running"}`

### Logs
- Monitor Railway logs for errors
- Check bot activity logs
- Monitor database connection logs

### Performance
- Monitor response times
- Check memory usage
- Monitor database performance

## Security Notes

- Never commit sensitive data to Git
- Use Railway's environment variable system
- Regularly rotate bot tokens
- Monitor admin access logs
- Keep dependencies updated
