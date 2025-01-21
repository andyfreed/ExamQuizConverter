import streamlit as st
import pandas as pd
import io
from parser import ExamParser
import chardet

# Set page config at the very beginning
st.set_page_config(
    page_title="Exam Question Converter",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add headers for iframe embedding
def add_iframe_headers():
    st.markdown("""
        <style>
            header {display: none !important;}
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# Call the function to add headers
add_iframe_headers()

def detect_encoding(file_bytes):
    """Detect the encoding of the uploaded file."""
    result = chardet.detect(file_bytes)
    return result['encoding']

def read_file_content(uploaded_file):
    """Read file content with appropriate encoding."""
    try:
        # Read the file as bytes first
        bytes_data = uploaded_file.getvalue()

        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
        content = None
        used_encoding = None

        for encoding in encodings:
            try:
                content = bytes_data.decode(encoding)
                used_encoding = encoding
                st.success(f"Successfully read file using {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            # If no encoding worked, try chardet as a last resort
            detected = chardet.detect(bytes_data)
            try:
                content = bytes_data.decode(detected['encoding'] if detected['encoding'] else 'utf-8')
                used_encoding = detected['encoding']
                st.success(f"Successfully read file using detected encoding: {detected['encoding']}")
            except:
                raise UnicodeDecodeError("Could not decode file with any supported encoding")

        return content, None
    except Exception as e:
        detailed_error = f"Error reading file: {str(e)}\nTried encodings: {encodings}"
        return None, detailed_error

def main():
    st.title("📝 Exam Question Converter")
    st.write("Convert exam questions from text format to structured spreadsheet")

    # Add notice about file format
    st.info("Please note: Only .txt files are accepted for both exam questions and answer keys.")

    # Add checkbox for separate answer key
    has_separate_answers = st.checkbox("I have a separate answer key file")

    # File upload for questions - only accept .txt
    uploaded_file = st.file_uploader("Upload your exam question file", type=['txt'])

    if uploaded_file is not None and not uploaded_file.name.lower().endswith('.txt'):
        st.error("Error: Please upload only .txt files for exam questions.")
        return

    # Answer key file upload (if checkbox is checked) - only accept .txt
    answer_key_file = None
    if has_separate_answers:
        answer_key_file = st.file_uploader("Upload your answer key file", type=['txt'])

        if answer_key_file is not None and not answer_key_file.name.lower().endswith('.txt'):
            st.error("Error: Please upload only .txt files for answer keys.")
            return

    if uploaded_file:
        # Read and parse file
        content, error = read_file_content(uploaded_file)

        if error:
            st.error(error)
        else:
            try:
                # Initialize parser
                parser = ExamParser()

                # If we have a separate answer key, read and process it
                answer_key_content = None
                if has_separate_answers and answer_key_file:
                    answer_key_content, key_error = read_file_content(answer_key_file)
                    if key_error:
                        st.error(f"Error reading answer key file: {key_error}")
                        return

                # Parse content with optional answer key
                df = parser.process_file(content, answer_key_content if has_separate_answers else None)

                # Preview the data
                st.subheader("Preview of Parsed Questions")
                st.dataframe(df)

                if not df.empty:
                    # Export options
                    st.subheader("Export Options")

                    # Create download buttons
                    col1, col2 = st.columns(2)

                    with col1:
                        # Excel export
                        excel_buffer = io.BytesIO()
                        df.to_excel(excel_buffer, index=False)
                        excel_data = excel_buffer.getvalue()

                        st.download_button(
                            label="Download as Excel",
                            data=excel_data,
                            file_name="exam_questions.xlsx",
                            mime="application/vnd.ms-excel"
                        )

                    with col2:
                        # CSV export
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download as CSV",
                            data=csv,
                            file_name="exam_questions.csv",
                            mime="text/csv"
                        )

                    # Display statistics
                    st.subheader("File Statistics")
                    st.write(f"Total questions parsed: {len(df)}")

                    # Show questions with missing data
                    missing_answers = df[df[['answer choice A', 'answer choice B', 'answer choice C', 'answer choice D']].isna().any(axis=1)]
                    if not missing_answers.empty:
                        st.warning(f"Found {len(missing_answers)} questions with missing answer choices")

                    missing_correct = df[df['Correct Answer'].isna()]
                    if not missing_correct.empty:
                        st.warning(f"Found {len(missing_correct)} questions with missing correct answers")

            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
                st.write("Please make sure the file follows the expected format.")

    # Add usage instructions
    with st.expander("📖 Usage Instructions"):
        st.markdown("""
            ### File Format Requirements:
            - Only .txt files are accepted for both exam questions and answer keys
            - Files must be plain text format with proper encoding

            ### Expected Question Format:
            1. Each question should start with a number followed by a period (e.g., "1.", "2.", etc.)
            2. Questions can be consecutive without blank lines in between
            3. Each answer choice should be on a new line, starting with A, B, C, or D
            4. Mark the correct answer with an asterisk (*) OR upload a separate answer key file

            ### Example Format for Questions:
            ```
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
            ```

            ### Example Format for Answer Key:
            ```
            1. C
            2. D
            ```

            ### Output Format:
            The converted file will contain the following columns:
            - Question
            - answer choice A
            - answer choice B
            - answer choice C
            - answer choice D
            - Correct Answer (shows the full text of the correct answer)
            """)

if __name__ == '__main__':
    main()