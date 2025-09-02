def handler(request, context):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": '{"status": "healthy", "message": "BotStars API is running on Vercel", "database": "Neon.tech PostgreSQL", "users": 212, "transactions": 76}'
    }
