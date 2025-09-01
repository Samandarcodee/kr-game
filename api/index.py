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
    return VercelHandler(request, context)

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
