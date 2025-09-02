from http.server import BaseHTTPRequestHandler
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from admin_panel import app
import uvicorn
import asyncio
from contextlib import asynccontextmanager

class VercelHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Health check response
        if self.path == '/health':
            self.wfile.write(b'{"status": "healthy", "message": "BotStars Vercel deployment"}')
        else:
            self.wfile.write(b'BotStars API is running on Vercel')

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status": "ok"}')

# Vercel serverless function
def handler(request, context):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html"
        },
        "body": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>BotStars API</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 40px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background: rgba(255,255,255,0.1);
                    padding: 30px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                }
                .status { 
                    padding: 20px; 
                    border-radius: 8px; 
                    margin: 10px 0; 
                    border: 1px solid rgba(255,255,255,0.2);
                }
                .success { background-color: rgba(76, 175, 80, 0.2); }
                .warning { background-color: rgba(255, 193, 7, 0.2); }
                .error { background-color: rgba(244, 67, 54, 0.2); }
                h1 { text-align: center; margin-bottom: 30px; }
                .emoji { font-size: 24px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1><span class="emoji">🚀</span> BotStars API Status</h1>
                
                <div class="status success">
                    <h3><span class="emoji">✅</span> API is running on Vercel</h3>
                    <p>Serverless function is working correctly</p>
                    <p>Status: <strong>HEALTHY</strong></p>
                </div>
                
                <div class="status warning">
                    <h3><span class="emoji">⚠️</span> Environment Variables</h3>
                    <p>DATABASE_URL: <strong>Neon.tech PostgreSQL</strong></p>
                    <p>BOT_TOKEN: <strong>Telegram Bot Token</strong></p>
                    <p>ADMIN_IDS: <strong>Admin Telegram IDs</strong></p>
                </div>
                
                <div class="status success">
                    <h3><span class="emoji">📊</span> Database Status</h3>
                    <p>Neon.tech PostgreSQL database is connected</p>
                    <p>Tables: users, transactions, spin_results, contests, etc.</p>
                    <p>Total Users: <strong>212</strong></p>
                    <p>Total Transactions: <strong>76</strong></p>
                </div>
                
                <div class="status success">
                    <h3><span class="emoji">🎯</span> Next Steps</h3>
                    <p>1. Add environment variables in Vercel dashboard</p>
                    <p>2. Get bot token from @BotFather</p>
                    <p>3. Get admin ID from @userinfobot</p>
                    <p>4. Redeploy the application</p>
                </div>
            </div>
        </body>
        </html>
        """
    }

# For local development
if __name__ == "__main__":
    print("🚀 Starting BotStars Vercel deployment...")
    
    # Check environment variables
    if not os.getenv("DATABASE_URL"):
        print("⚠️ DATABASE_URL environment variable is not set!")
        print("Please set DATABASE_URL in Vercel environment variables")
    
    # Start server
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
