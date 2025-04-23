#!/bin/bash

# Exit on error
set -e

echo "Starting Digital Ocean deployment..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Get the port from environment variable or use default
PORT=${PORT:-8080}
echo "Using port: $PORT"

# Create a simple HTTP server for health checks
cat > healthcheck_server.py << 'EOF'
import http.server
import socketserver
import threading
import time
import os
import sys
import subprocess
import signal

# Get port from environment or use default
PORT = int(os.environ.get("PORT", 8080))

# Define handler for health check requests
class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress log messages
        return

print(f"Starting health check server on port {PORT}")
handler = HealthCheckHandler
httpd = socketserver.TCPServer(("", PORT), handler)

# Start Streamlit in the background
streamlit_cmd = [
    "streamlit", "run", "app.py",
    "--server.port", "8501",  # Use a different port for Streamlit
    "--server.address", "0.0.0.0",
    "--server.headless", "true",
    "--server.enableCORS", "false",
    "--server.enableXsrfProtection", "false"
]

print("Starting Streamlit application...")
streamlit_process = subprocess.Popen(streamlit_cmd)

# Handle termination signals
def signal_handler(sig, frame):
    print("Shutting down...")
    if streamlit_process:
        streamlit_process.terminate()
    httpd.shutdown()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Run the health check server
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    httpd.server_close()
    if streamlit_process:
        streamlit_process.terminate()
EOF

# Run the health check server
echo "Starting server..."
python healthcheck_server.py 