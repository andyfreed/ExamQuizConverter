#!/bin/bash

# Exit on error
set -e

echo "Starting deployment script..."

# Make the script executable
chmod +x startup.sh

# Create and activate virtual environment
echo "Setting up Python virtual environment..."
python -m venv .venv
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Get the port from environment variable or use default
PORT=${PORT:-8000}
echo "Using port: $PORT"

# Start Streamlit with all necessary configurations
echo "Starting Streamlit application..."
streamlit run main.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --server.baseUrlPath "" \
    --browser.serverAddress "0.0.0.0" \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --server.maxUploadSize 200 