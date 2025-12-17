from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
import re

# Helper to remove HTML tags and decode entities
def clean_html(raw_html):
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    # Basic entity decoding
    cleantext = cleantext.replace('&quot;', '"').replace('&apos;', "'").replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&middot;', '·')
    return cleantext

def parse_pubdate(pubdate_str):
    # Format: "Tue, 17 Dec 2025 09:00:00 +0900"
    try:
        return datetime.strptime(pubdate_str, "%a, %d %b %Y %H:%M:%S %z")
    except Exception as e:
        return None

def process_news_search(client_id, client_secret, keywords, display_count=50):
    # 14 days ago check
    now = datetime.now().astimezone() # Local aware
    fourteen_days_ago = now - timedelta(days=14)

    final_results = {}

    for keyword in keywords:
        try:
            encText = urllib.parse.quote(keyword)
            url = f"https://openapi.naver.com/v1/search/news.json?query={encText}&display={display_count}&sort=date"
            
            req = urllib.request.Request(url)
            req.add_header("X-Naver-Client-Id", client_id)
            req.add_header("X-Naver-Client-Secret", client_secret)
            
            response = urllib.request.urlopen(req)
            rescode = response.getcode()
            
            if rescode == 200:
                response_body = response.read()
                data = json.loads(response_body.decode('utf-8'))
                items = data.get('items', [])
                
                seen_links = set()
                seen_titles = set()

                # Parse and Sort
                parsed_items = []
                for item in items:
                    p_date = parse_pubdate(item['pubDate'])
                    if not p_date: continue
                    
                    parsed_items.append({
                        'original': item,
                        'date': p_date
                    })
                
                # Sort descending (Latest first)
                parsed_items.sort(key=lambda x: x['date'], reverse=True)

                processed_items = []
                for p_item in parsed_items:
                    item = p_item['original']
                    p_date = p_item['date']

                    # Filter 14 days
                    if p_date < fourteen_days_ago:
                        continue

                    # Clean features
                    title = clean_html(item['title'])
                    link = item['link']
                    
                    # Deduplication
                    if link in seen_links: continue
                    if title in seen_titles: continue
                    
                    seen_links.add(link)
                    seen_titles.add(title)
                    
                    # Format output
                    processed_items.append({
                        'title': title,
                        'link': link,
                        'pubDate': p_date.strftime("%Y-%m-%d %H:%M:%S"),
                        'description': clean_html(item['description'])
                    })
                
                final_results[keyword] = processed_items
            else:
                final_results[keyword] = []
        except Exception as e:
            # print(f"Error for {keyword}: {e}")
            final_results[keyword] = []
            
    return final_results

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Setup CORS and Headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        # 2. Check Environment Variables
        CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
        CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
        
        if not CLIENT_ID or not CLIENT_SECRET:
            self.wfile.write(json.dumps({"error": "Missing Server API Keys"}).encode('utf-8'))
            return

        # 3. Parse Request Body
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))
        except:
            self.wfile.write(json.dumps({"error": "Invalid Request"}).encode('utf-8'))
            return

        keywords = body.get('keywords', [])
        display_count = body.get('display', 50)
        
        # 4. Process
        results = process_news_search(CLIENT_ID, CLIENT_SECRET, keywords, display_count)
        
        # 5. Return JSON
        self.wfile.write(json.dumps(results).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
