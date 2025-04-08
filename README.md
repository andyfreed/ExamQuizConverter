# Question Converter Tool

A tool for converting and formatting questions in various formats. This application helps educators and content creators to easily transform their questions between different formats and styles.

## Features

- Question format conversion
- Multiple input/output format support
- User-friendly interface
- Streamlit-based web application
- Multi-app support in single Azure instance

## Project Structure

```
QuestionConverterTool/
├── apps/                     # Directory for all applications
│   └── question_converter.py # Question converter application
├── main.py                   # Main router for multiple apps
├── requirements.txt          # Project dependencies
└── utils.py                  # Shared utilities
```

## Adding New Apps

1. Create a new Python file in the `apps` directory
2. Add a `main()` function to your app
3. Import and add it to the `APPS` dictionary in `main.py`:
```python
from new_app import main as new_app_main

APPS = {
    "Question Converter": question_converter_app,
    "New App": new_app_main,
}
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/andyfreed/QuestionConverterTool.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application using:
```bash
streamlit run main.py
```

## Deployment

The application is deployed on Azure App Service and automatically updates when changes are pushed to the main branch on GitHub.

## License

This project is open source and available under the MIT License. 