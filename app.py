import streamlit as st
import pandas as pd
import io
from parser import ExamParser
import chardet

st.set_page_config(
    page_title="Exam Question Converter",
    page_icon="📝",
    layout="wide"
)

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

        # Debug information
        if content:
            st.write(f"File size: {len(bytes_data)} bytes")
            st.write(f"Used encoding: {used_encoding}")
            # Show first few characters for verification
            preview_length = min(200, len(content))
            st.text("File preview (first 200 chars):")
            st.code(content[:preview_length])

        return content, None
    except Exception as e:
        detailed_error = f"Error reading file: {str(e)}\nTried encodings: {encodings}"
        return None, detailed_error

def main():
    st.title("📝 Exam Question Converter")
    st.write("Convert exam questions from text format to structured spreadsheet")

    # File upload
    uploaded_file = st.file_uploader("Upload your exam question file", type=['txt'])

    if uploaded_file:
        # Read and parse file
        content, error = read_file_content(uploaded_file)

        if error:
            st.error(error)
        else:
            try:
                # Parse content
                parser = ExamParser()
                df = parser.process_file(content)

                # Debug: Print parsing results
                st.write(f"Debug: Number of questions parsed: {len(df)}")
                if len(df) == 0:
                    st.write("Debug: No questions were parsed from the content")

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
            ### Expected File Format:
            1. Each question should start with a number followed by a period (e.g., "1.", "2.", etc.)
            2. Questions can be consecutive without blank lines in between
            3. Each answer choice should be on a new line, starting with A, B, C, or D
            4. Mark the correct answer with an asterisk (*) either at the beginning or end of the answer

            ### Example Format:
            ```
            1. What is the present value of an annuity?
            A. The future value of all payments
            B. The sum of all payments
            C. *The current worth of all future payments
            D. The average of all payments

            2. Which factor affects annuity calculations?
            A. Interest rate
            B. Payment frequency
            C. Time period
            D. All of the above*
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