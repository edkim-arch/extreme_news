import http.server
import socketserver
import os
import sys
import json

# Load Environment Variables from ../.env (Mocking Vercel Env)
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    print(f"Loading env from: {os.path.abspath(env_path)}")
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    else:
        print("Warning: .env file not found in parent directory.")

# Import the process logic from api/news.py
# Use relative import if running as module, or sys.path hack if running as script
try:
    from api.news import process_news_search
except ImportError:
    # Fallback if run from different dir
    sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
    from news import process_news_search

class LocalHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        # Handle API Route
        if self.path.startswith('/api/news'):
            # 1. Read Body (SimpleHTTPRequestHandler usually hasn't consumed it yet)
            length = int(self.headers.get('Content-Length', 0))
            if length > 0:
                body_data = self.rfile.read(length)
                try:
                    body_json = json.loads(body_data.decode('utf-8'))
                except:
                    self.send_error(400, "Invalid JSON")
                    return
            else:
                body_json = {}

            # 2. Extract Params
            keywords = body_json.get('keywords', [])
            display = body_json.get('display', 50)

            # 3. Call Logic
            # Load keys from env
            client_id = os.environ.get("NAVER_CLIENT_ID")
            client_secret = os.environ.get("NAVER_CLIENT_SECRET")

            if not client_id or not client_secret:
                self.send_error(500, "Server Keys Missing")
                return

            result = process_news_search(client_id, client_secret, keywords, display)

            # 4. Send Response
            response_bytes = json.dumps(result).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(response_bytes))
            self.end_headers()
            self.wfile.write(response_bytes)
            return
        
        # Default behavior (Static Files)
        super().do_POST()

    def do_GET(self):
        # Serve index.html for root
        if self.path == '/':
            self.path = '/index.html'
        super().do_GET()

if __name__ == "__main__":
    load_env()
    PORT = 8000
    print(f"Starting Local Server at http://localhost:{PORT}")
    with socketserver.TCPServer(("", PORT), LocalHandler) as httpd:
        httpd.serve_forever()
