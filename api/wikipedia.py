from http.server import BaseHTTPRequestHandler
import requests
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        query = data.get('query', '')
        
        # Extract the topic from the query (after "wikipedia")
        parts = query.lower().split('wikipedia')
        if len(parts) < 2:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Please provide a topic to search for"}).encode())
            return
            
        topic = parts[1].strip()
        
        try:
            # Fetch Wikipedia summary
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
            response = requests.get(url, timeout=10)
            wiki_data = response.json()
            summary = wiki_data.get('extract', 'No summary available')
            
            result = {"response": summary}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())