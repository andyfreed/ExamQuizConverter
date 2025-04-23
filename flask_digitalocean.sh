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

# Create a WSGI file for gunicorn
cat > wsgi.py << 'EOF'
from flask_app import app

if __name__ == "__main__":
    app.run()
EOF

# Start the Flask app with gunicorn directly on the required port
echo "FLASK APP DEPLOYMENT: Starting Flask app with Gunicorn on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT wsgi:app 