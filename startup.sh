#!/bin/bash

# Exit on error
set -e

echo "Starting deployment script..."

# Activate virtual environment
source antenv/bin/activate

# Install dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Get the port from environment variable or use default
PORT=${PORT:-8000}
echo "Using port: $PORT"

# Create log directory if it doesn't exist
mkdir -p /home/site/wwwroot/logs

# Start Streamlit with proper logging
echo "Starting Streamlit application..."
nohup streamlit run main.py \
  --server.port $PORT \
  --server.address 0.0.0.0 \
  --server.headless true \
  > /home/site/wwwroot/logs/streamlit.log 2>&1 &

# Wait for Streamlit to start
echo "Waiting for Streamlit to start..."
sleep 10

# Check if Streamlit is running
if ! pgrep -f "streamlit run"; then
  echo "Error: Streamlit failed to start. Check logs:"
  cat /home/site/wwwroot/logs/streamlit.log
  exit 1
fi

echo "Streamlit started successfully"
exit 0 