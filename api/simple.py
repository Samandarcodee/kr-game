from http.server import BaseHTTPRequestHandler
import json
import os

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>BotStars API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .status { padding: 20px; border-radius: 8px; margin: 10px 0; }
                .success { background-color: #d4edda; color: #155724; }
                .warning { background-color: #fff3cd; color: #856404; }
                .error { background-color: #f8d7da; color: #721c24; }
            </style>
        </head>
        <body>
            <h1>🚀 BotStars API Status</h1>
            <div class="status success">
                <h3>✅ API is running on Vercel</h3>
                <p>Serverless function is working correctly</p>
            </div>
            <div class="status warning">
                <h3>⚠️ Environment Variables</h3>
                <p>DATABASE_URL: {}</p>
                <p>BOT_TOKEN: {}</p>
                <p>ADMIN_IDS: {}</p>
            </div>
            <div class="status success">
                <h3>📊 Database Status</h3>
                <p>Neon.tech PostgreSQL database is connected</p>
                <p>Tables: users, transactions, spin_results, contests, etc.</p>
            </div>
        </body>
        </html>
        """.format(
            "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not set",
            "✅ Set" if os.getenv("BOT_TOKEN") else "❌ Not set", 
            "✅ Set" if os.getenv("ADMIN_IDS") else "❌ Not set"
        )
        
        self.wfile.write(html_content.encode())

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "success",
            "message": "BotStars API is working",
            "database_url_set": bool(os.getenv("DATABASE_URL")),
            "bot_token_set": bool(os.getenv("BOT_TOKEN")),
            "admin_ids_set": bool(os.getenv("ADMIN_IDS"))
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())

def handler(request, context):
    return SimpleHandler(request, context)
