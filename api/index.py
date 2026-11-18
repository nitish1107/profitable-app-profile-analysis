from http.server import BaseHTTPRequestHandler
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "public", "data.json")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                payload = json.load(f)
        else:
            payload = {"status": "online", "message": "App Intelligence API Live"}

        if self.path == '/api/summary':
            response = payload.get('summary', {})
        elif self.path == '/api/categories':
            response = payload.get('categories', [])
        elif self.path == '/api/benchmark':
            response = payload.get('benchmarks', {})
        else:
            response = payload

        self.wfile.write(json.dumps(response).encode('utf-8'))
