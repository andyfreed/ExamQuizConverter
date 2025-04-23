import http.server
import socketserver
import threading
import requests
import time
import os

PORT = int(os.environ.get("PORT", 8080))
STREAMLIT_PORT = 8080  # Hardcoded to match our Streamlit config

class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            try:
                # Try to connect to the Streamlit app
                requests.get(f"http://localhost:{STREAMLIT_PORT}", timeout=2)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"OK")
            except:
                self.send_response(503)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Service Unavailable")
        else:
            self.send_response(404)
            self.end_headers()

def run_health_server():
    handler = HealthCheckHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Health check server running at port {PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    # Start health check server in a separate thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Keep the main thread alive
    while True:
        time.sleep(60) 