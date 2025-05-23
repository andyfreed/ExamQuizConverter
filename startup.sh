#!/bin/bash

# Exit on error
set -e

echo "Starting deployment script..."

# Ensure script is executable
chmod +x "$0"

# Activate virtual environment
source antenv/bin/activate || {
    echo "Error: Failed to activate virtual environment"
    exit 1
}

# Install dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Get the port from environment variable or use default
PORT=${PORT:-8000}
echo "Using port: $PORT"

# Create log directory if it doesn't exist
mkdir -p /home/site/wwwroot/logs

# Kill any existing Streamlit processes
echo "Cleaning up any existing Streamlit processes..."
pkill -f "streamlit run" || true

# Start Streamlit with proper logging
echo "Starting Streamlit application..."
streamlit run main.py \
  --server.port $PORT \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  > /home/site/wwwroot/logs/streamlit.log 2>&1 