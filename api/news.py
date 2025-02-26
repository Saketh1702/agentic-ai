from http.server import BaseHTTPRequestHandler
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        query = data.get('query', '')
        
        # Extract the keyword from the query (after "news")
        parts = query.lower().split('news')
        if len(parts) < 2:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Please provide a topic to search for"}).encode())
            return
            
        keyword = parts[1].strip()
        
        try:
            # Fetch news articles
            api_key = os.getenv('NEWS_API_KEY')
            if not api_key:
                raise ValueError("NEWS API key not found")
                
            url = f'https://newsapi.org/v2/everything?q={keyword}&apiKey={api_key}&pageSize=5'
            response = requests.get(url, timeout=10)
            news_data = response.json()
            articles = news_data.get('articles', [])
            
            if not articles:
                result = {"response": "No articles found"}
            else:
                formatted_articles = [
                    f"{i+1}. {article.get('title')} - {article.get('source').get('name')}" 
                    for i, article in enumerate(articles)
                ]
                result = {"response": "\n".join(formatted_articles)}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())