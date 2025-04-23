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

# Make sure assets directory exists
mkdir -p attached_assets

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

def start_server():
    print(f"Starting health check server on port {PORT}")
    try:
        handler = HealthCheckHandler
        httpd = socketserver.TCPServer(("0.0.0.0", PORT), handler)
        httpd.serve_forever()
    except Exception as e:
        print(f"Error starting health check server: {e}")
        sys.exit(1)

# Start the health check server in a separate thread
server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

# Start Streamlit in the main thread
streamlit_cmd = [
    "streamlit", "run", "app.py",
    "--server.port", "8501",  # Use a different port for Streamlit
    "--server.address", "0.0.0.0",
    "--server.headless", "true",
    "--server.enableCORS", "false",
    "--server.enableXsrfProtection", "false"
]

print("Starting Streamlit application...")
try:
    # Give the health check server time to start
    time.sleep(2)
    # Execute Streamlit directly (not as a subprocess)
    os.execvp(streamlit_cmd[0], streamlit_cmd)
except Exception as e:
    print(f"Error starting Streamlit: {e}")
    sys.exit(1)
EOF

# Run the server
echo "Starting server..."
python healthcheck_server.py 