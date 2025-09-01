from http.server import BaseHTTPRequestHandler
import json
import os

class VercelHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "healthy",
            "message": "BotStars API is running on Vercel",
            "database_url_set": bool(os.getenv("DATABASE_URL")),
            "bot_token_set": bool(os.getenv("BOT_TOKEN")),
            "admin_ids_set": bool(os.getenv("ADMIN_IDS"))
        }
        
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "ok",
            "message": "POST request received"
        }
        
        self.wfile.write(json.dumps(response).encode())

def handler(request, context):
    return VercelHandler(request, context)
