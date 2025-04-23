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

# Start Streamlit with proper configuration for Digital Ocean
echo "Starting Streamlit application..."
streamlit run app.py \
  --server.port $PORT \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false 