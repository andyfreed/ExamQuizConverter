# Exam Quiz Converter

A Streamlit application for converting exam questions between different formats.

## Features

- Convert questions from various formats
- Support for multiple choice questions
- Interactive web interface

## Local Development

1. Clone this repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `streamlit run app.py`

## Deploying to Digital Ocean

### Using App Platform

1. Push your code to GitHub
2. Log in to Digital Ocean
3. Go to the App Platform section
4. Click "Create App" and select your GitHub repository
5. Select Python as the environment
6. Set the build command: `pip install -r requirements.txt`
7. Set the run command: `streamlit run app.py --server.port 8080 --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false`
8. For Health Checks:
   - Make sure to configure the health check URL to `/`
   - Set the port to `8080`
9. Deploy the app

### Using a Droplet

1. Create a new Droplet with Ubuntu
2. SSH into your Droplet
3. Install Python and pip:
   ```
   sudo apt update
   sudo apt install python3-pip python3-venv
   ```
4. Clone your repository:
   ```
   git clone <your-repository-url>
   cd ExamQuizConverter
   ```
5. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
6. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
7. Install tmux to keep the app running:
   ```
   sudo apt install tmux
   ```
8. Start a new tmux session:
   ```
   tmux new -s streamlit
   ```
9. Run the application:
   ```
   streamlit run app.py --server.port 8080 --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false
   ```
10. Detach from the tmux session by pressing `Ctrl+B` and then `D`

## Flask Version

This application now has a Flask-based alternative implementation in `flask_app.py`. The Flask version
provides the same functionality as the Streamlit version but may be more compatible with some hosting environments.

### Running the Flask Version

1. Install the required dependencies: `pip install -r requirements.txt`
2. Run the Flask app: `python flask_app.py`
3. Open your browser to `http://localhost:5000`

### Deploying the Flask Version to DigitalOcean

1. Push your code to GitHub
2. Log in to DigitalOcean
3. Go to the App Platform section
4. Click "Create App" and select your GitHub repository
5. Select Python as the environment
6. Use the `flask_digitalocean.sh` script for deployment
7. For Health Checks:
   - Make sure to configure the health check URL to `/`
   - Set the port to `8080`
8. Deploy the app

## Usage

1. Open the application in your web browser
2. Upload your exam question file
3. Select conversion options
4. Download the converted file 