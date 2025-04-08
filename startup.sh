#!/bin/bash

# Exit on error
set -e

echo "Starting deployment script..."

# Activate Python virtual environment if it exists
if [ -d "antenv" ]; then
    echo "Activating virtual environment..."
    source antenv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Get the port from environment variable or use default
PORT=${PORT:-8000}
echo "Using port: $PORT"

# Make sure the .streamlit directory exists
mkdir -p .streamlit

# Start Streamlit with explicit host binding
echo "Starting Streamlit application..."
streamlit run main.py --server.address 0.0.0.0 --server.port $PORT --server.headless true 