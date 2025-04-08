#!/bin/bash

# Exit on error
set -e

echo "Starting deployment script..."

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Get the port from environment variable or use default
PORT=${WEBSITES_PORT:-8000}
echo "Using port: $PORT"

# Start Streamlit with minimal configuration
echo "Starting Streamlit application..."
streamlit run main.py --server.port $PORT 