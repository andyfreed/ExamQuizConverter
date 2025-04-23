import streamlit.web.cli as stcli
import http.server
import socketserver
import threading
import time
import os
import sys

# Get port from environment or use default
PORT = int(os.environ.get("PORT", 8080))
print(f"Using port: {PORT}")

# Define handler for health check requests
class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Health Check OK")
            print(f"Health check request received on {self.path}")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Use print instead of suppressing completely
        print(f"Health check: {format % args}")

def run_health_check_server():
    """Run the health check server in a separate thread"""
    try:
        print(f"Starting health check server on port {PORT}")
        server = socketserver.TCPServer(("0.0.0.0", PORT), HealthCheckHandler)
        server.serve_forever()
    except Exception as e:
        print(f"Error in health check server: {e}")
        sys.exit(1)

def run_streamlit():
    """Run the Streamlit application"""
    print("Starting Streamlit application...")
    # Use Streamlit's own CLI to run the app
    sys.argv = ["streamlit", "run", "app.py", 
                "--server.port", "8501",
                "--server.address", "0.0.0.0",
                "--server.headless", "true",
                "--server.enableCORS", "false",
                "--server.enableXsrfProtection", "false"]
    stcli.main()

if __name__ == "__main__":
    # Create assets directory
    os.makedirs("attached_assets", exist_ok=True)
    
    # Start health check server thread
    health_thread = threading.Thread(target=run_health_check_server)
    health_thread.daemon = True
    health_thread.start()
    
    # Give the health check server time to start
    time.sleep(3)
    
    # Make sure it's running
    print("Health check server should be running now")
    
    # Run Streamlit in the main thread
    run_streamlit() 