#!/bin/bash
set -e

echo "FLASK APP DEPLOYMENT: Starting Flask app deployment on DigitalOcean..."

# Make sure assets directory exists
mkdir -p attached_assets

# Install dependencies
echo "FLASK APP DEPLOYMENT: Installing dependencies..."
pip install -r requirements.txt
pip install gunicorn  # Ensure gunicorn is installed

# Get the port from environment variable or use default
PORT=${PORT:-8080}
echo "FLASK APP DEPLOYMENT: Using port: $PORT"

# Create a dual-purpose script that runs both the health check and Flask
cat > run_both.py << 'EOF'
import http.server
import socketserver
import os
import threading
import subprocess
import time
import sys
from flask_app import app

# Get port from environment
PORT = int(os.environ.get("PORT", 8080))

class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"Health check received on path: {self.path}")
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"OK")
    
    def log_message(self, format, *args):
        print(f"Health check: {args}")

def run_health_server():
    """Run the health check server in a thread"""
    server = socketserver.TCPServer(("0.0.0.0", PORT), HealthHandler)
    print(f"FLASK APP DEPLOYMENT: Health check server running on port {PORT}")
    server.serve_forever()

def run_flask_app():
    """Run the Flask app on a different port"""
    # We'll use the app directly from the import at the top
    print("FLASK APP DEPLOYMENT: Starting Flask app on port 5000")
    app.run(host="0.0.0.0", port=5000, debug=False)

if __name__ == "__main__":
    # Start health server in a background thread
    health_thread = threading.Thread(target=run_health_server)
    health_thread.daemon = True
    health_thread.start()
    
    # Wait for health server to initialize
    time.sleep(2)
    
    # Run Flask in the main thread
    run_flask_app()
EOF

# Run the combined script
python run_both.py 