import re
import chardet

def detect_encoding(file_bytes):
    """Detect the encoding of a file's bytes."""
    result = chardet.detect(file_bytes)
    return result['encoding']

def clean_text(text):
    """Clean text by removing extra whitespace and normalizing line endings."""
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove empty lines
    text = re.sub(r'\n\s*\n', '\n', text)
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text.strip()

def extract_question_number(text):
    """Extract question number from text."""
    match = re.match(r'(\d+)\.?\s*', text)
    return int(match.group(1)) if match else None 