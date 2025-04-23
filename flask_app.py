from flask import Flask, request, render_template_string, send_file
import io
from parser import ExamParser
import pandas as pd
import chardet
from docx import Document
import re
import os

app = Flask(__name__)

# Create assets directory if it doesn't exist
if not os.path.exists("attached_assets"):
    os.makedirs("attached_assets", exist_ok=True)

# Define the HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Exam Question Converter</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 { 
            color: #2c3e50;
            text-align: center;
        }
        .container {
            background-color: #f8f9fa;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .info-box {
            background-color: #e3f2fd;
            border-left: 5px solid #2196f3;
            padding: 10px 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .success-box {
            background-color: #e8f5e9;
            border-left: 5px solid #4caf50;
            padding: 10px 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .warning-box {
            background-color: #fff8e1;
            border-left: 5px solid #ff9800;
            padding: 10px 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .error-box {
            background-color: #ffebee;
            border-left: 5px solid #f44336;
            padding: 10px 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        button, .button {
            background-color: #4caf50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px 0;
            text-decoration: none;
            display: inline-block;
        }
        button:hover, .button:hover {
            background-color: #45a049;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .file-upload {
            margin: 20px 0;
        }
        details {
            margin: 20px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }
        summary {
            font-weight: bold;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 Exam Question Converter</h1>
        <p>Convert exam questions from text format to structured spreadsheet</p>
        
        <div class="info-box">
            Questions must be in .txt format. Answer keys can be in .txt or .docx format.
        </div>
        
        <form method="POST" enctype="multipart/form-data">
            <div class="file-upload">
                <label for="has_separate_answers">
                    <input type="checkbox" id="has_separate_answers" name="has_separate_answers"> 
                    I have a separate answer key file
                </label>
            </div>
            
            <div class="file-upload">
                <label for="question_file">Upload your exam question file (.txt):</label><br>
                <input type="file" id="question_file" name="question_file" accept=".txt" required>
            </div>
            
            <div class="file-upload" id="answer_key_div" style="display: none;">
                <label for="answer_key_file">Upload your answer key file (.txt, .docx):</label><br>
                <input type="file" id="answer_key_file" name="answer_key_file" accept=".txt,.docx">
            </div>
            
            <button type="submit">Process Files</button>
        </form>
        
        {% if error %}
            <div class="error-box">{{ error }}</div>
        {% endif %}
        
        {% if success %}
            <div class="success-box">{{ success }}</div>
        {% endif %}
        
        {% if df_html %}
            <h2>Preview of Parsed Questions</h2>
            {{ df_html|safe }}
            
            <h2>Export Options</h2>
            <a href="/download/excel" class="button">Download as Excel</a>
            <a href="/download/csv" class="button">Download as CSV</a>
            
            <div class="success-box">
                Processing complete! 🎉
            </div>
            
            <h2>File Statistics</h2>
            <p>Total questions parsed: {{ total_questions }}</p>
            
            {% if missing_answers > 0 %}
                <div class="warning-box">
                    Found {{ missing_answers }} questions with missing answer choices
                </div>
            {% endif %}
            
            {% if missing_correct > 0 %}
                <div class="warning-box">
                    Found {{ missing_correct }} questions with missing correct answers
                </div>
            {% endif %}
        {% endif %}
        
        <details>
            <summary>📖 Usage Instructions</summary>
            <div>
                <h3>File Format Requirements:</h3>
                <ul>
                    <li>Questions must be in .txt format</li>
                    <li>Answer keys can be in .txt or .docx format</li>
                    <li>Files must be properly formatted with clear question numbering</li>
                </ul>
                
                <h3>Expected Question Format:</h3>
                <ol>
                    <li>Each question should start with a number followed by a period (e.g., "1.", "2.", etc.)</li>
                    <li>Questions can be consecutive without blank lines in between</li>
                    <li>Each answer choice should be on a new line, starting with A, B, C, or D</li>
                    <li>Mark the correct answer with an asterisk (*) OR upload a separate answer key file</li>
                </ol>
                
                <h3>Example Format for Questions:</h3>
                <pre>
1. What is the present value of an annuity?
A. The future value of all payments
B. The sum of all payments
C. The current worth of all future payments
D. The average of all payments

2. Which factor affects annuity calculations?
A. Interest rate
B. Payment frequency
C. Time period
D. All of the above
                </pre>
                
                <h3>Example Format for Answer Key:</h3>
                <pre>
1. C
2. D
                </pre>
                
                <h3>Output Format:</h3>
                <p>The converted file will contain the following columns:</p>
                <ul>
                    <li>Question</li>
                    <li>answer choice A</li>
                    <li>answer choice B</li>
                    <li>answer choice C</li>
                    <li>answer choice D</li>
                    <li>Correct Answer (shows the full text of the correct answer)</li>
                </ul>
            </div>
        </details>
    </div>
    
    <script>
        // Show/hide answer key file upload based on checkbox
        document.getElementById('has_separate_answers').addEventListener('change', function() {
            document.getElementById('answer_key_div').style.display = this.checked ? 'block' : 'none';
        });
    </script>
</body>
</html>
"""

# Store the dataframe in memory for downloads
global_df = None

def read_docx_content(file_bytes):
    """Read content from a .docx file."""
    try:
        # Create a BytesIO object from the file bytes
        doc = Document(io.BytesIO(file_bytes))

        # Extract text from paragraphs and tables
        content = []

        # Process tables
        for table_idx, table in enumerate(doc.tables):
            for row_idx, row in enumerate(table.rows):
                row_text = [cell.text.strip() for cell in row.cells]

                # Skip empty rows
                if not any(row_text):
                    continue

                # Process each cell in the row
                for i in range(len(row_text)):
                    # Try to find question number and answer pairs
                    cell_text = row_text[i].strip()

                    # Skip empty cells
                    if not cell_text:
                        continue

                    # Check if this cell contains a question number
                    match = re.match(r'(\d+)\.?\s*$', cell_text)
                    if match and i + 1 < len(row_text):
                        question_num = match.group(1)
                        # Look at the next cell for the answer
                        answer = row_text[i + 1].strip()
                        if answer and re.match(r'^[A-Da-d]$', answer):
                            content.append(f"{question_num}: {answer}")

        # Join all content with newlines
        full_content = '\n'.join(content)

        # Clean up the content
        full_content = re.sub(r'\s+', ' ', full_content)  # Replace multiple spaces with single space
        full_content = re.sub(r'\n\s*\n', '\n', full_content)  # Remove empty lines

        return full_content, None
    except Exception as e:
        return None, f"Error reading .docx file: {str(e)}"

def read_file_content(file):
    """Read file content with appropriate encoding."""
    try:
        # Check if file is .docx
        if file.filename.lower().endswith('.docx'):
            return read_docx_content(file.read())

        # For .txt files, use existing logic
        bytes_data = file.read()
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
        content = None
        used_encoding = None

        for encoding in encodings:
            try:
                content = bytes_data.decode(encoding)
                used_encoding = encoding
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            detected = chardet.detect(bytes_data)
            try:
                content = bytes_data.decode(detected['encoding'] if detected['encoding'] else 'utf-8')
                used_encoding = detected['encoding']
            except:
                raise UnicodeDecodeError("Could not decode file with any supported encoding")

        return content, None
    except Exception as e:
        detailed_error = f"Error reading file: {str(e)}"
        return None, detailed_error

@app.route('/', methods=['GET', 'POST'])
def index_or_health():
    global global_df
    
    # Just return "OK" for simple health checks with no Accept header
    # This supports DigitalOcean's health checks
    if 'Accept' not in request.headers or request.headers['Accept'] == '*/*':
        return "OK"
    
    # Normal processing for browser requests
    if request.method == 'POST':
        # Check if files were uploaded
        if 'question_file' not in request.files:
            return render_template_string(HTML_TEMPLATE, error="No question file uploaded")
            
        question_file = request.files['question_file']
        if question_file.filename == '':
            return render_template_string(HTML_TEMPLATE, error="No question file selected")
            
        # Check if we have a separate answer key
        has_separate_answers = 'has_separate_answers' in request.form
        answer_key_file = None
        
        if has_separate_answers and 'answer_key_file' in request.files:
            answer_key_file = request.files['answer_key_file']
            if answer_key_file.filename == '':
                answer_key_file = None
                
        # Read and parse files
        content, error = read_file_content(question_file)
        
        if error:
            return render_template_string(HTML_TEMPLATE, error=error)
            
        try:
            # Initialize parser
            parser = ExamParser()
            
            # Process answer key if provided
            answer_key_content = None
            if has_separate_answers and answer_key_file:
                answer_key_content, key_error = read_file_content(answer_key_file)
                if key_error:
                    return render_template_string(HTML_TEMPLATE, error=f"Error reading answer key file: {key_error}")
                    
            # Parse content with optional answer key
            df = parser.process_file(content, answer_key_content if has_separate_answers else None)
            
            # Store dataframe for downloads
            global_df = df
            
            # Calculate statistics
            total_questions = len(df)
            missing_answers = len(df[df[['answer choice A', 'answer choice B', 'answer choice C', 'answer choice D']].isna().any(axis=1)])
            missing_correct = len(df[df['Correct Answer'].isna()])
            
            # Render template with results
            return render_template_string(
                HTML_TEMPLATE,
                success="Files processed successfully",
                df_html=df.to_html(classes='table table-striped'),
                total_questions=total_questions,
                missing_answers=missing_answers,
                missing_correct=missing_correct
            )
            
        except Exception as e:
            return render_template_string(HTML_TEMPLATE, error=f"Error processing file: {str(e)}")
            
    # GET request - show the form
    return render_template_string(HTML_TEMPLATE)

@app.route('/download/<format>')
def download(format):
    global global_df
    
    if global_df is None:
        return "No data available for download. Please process files first.", 400
        
    if format == 'excel':
        # Create Excel file
        output = io.BytesIO()
        global_df.to_excel(output, index=False)
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name="exam_questions.xlsx",
            mimetype="application/vnd.ms-excel"
        )
        
    elif format == 'csv':
        # Create CSV file
        output = io.BytesIO()
        output.write(global_df.to_csv(index=False).encode('utf-8'))
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name="exam_questions.csv",
            mimetype="text/csv"
        )
        
    else:
        return "Invalid format specified", 400

# Add a health check route
@app.route('/health')
def health_check():
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 