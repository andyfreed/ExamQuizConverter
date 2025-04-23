#!/bin/bash

# Exit on error
set -e

echo "Starting Digital Ocean deployment..."

# Make sure assets directory exists
mkdir -p attached_assets

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create a simple stand-alone health check server - WILL START FIRST
cat > health_server.py << 'EOF'
import http.server
import socketserver
import os
import threading
import sys

# Use the PORT environment variable
PORT = int(os.environ.get("PORT", 8080))

# Define a simple handler
class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
            print(f"Health check request received at {self.path}")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"Health check: {format % args}")

# Start the server
print(f"Starting health check server on port {PORT}")
try:
    httpd = socketserver.TCPServer(("0.0.0.0", PORT), Handler)
    httpd.serve_forever()
except Exception as e:
    print(f"Health check server error: {e}")
    sys.exit(1)
EOF

# Start health check server FIRST
nohup python health_server.py > health.log 2>&1 &

# Wait for health server to start
echo "Waiting for health check server to start..."
sleep 3

# Start streamlit directly
echo "Starting Streamlit application..."
exec streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false 