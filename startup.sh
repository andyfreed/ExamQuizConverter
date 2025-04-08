#!/bin/bash

# Make the script executable
chmod +x startup.sh

# Install dependencies
pip install -r requirements.txt

# Get the port from environment variable or use default
PORT=${PORT:-8000}

# Start Streamlit
streamlit run main.py --server.port $PORT --server.address 0.0.0.0 --server.baseUrlPath "" --browser.serverAddress "0.0.0.0" --server.enableCORS false --server.enableXsrfProtection false 