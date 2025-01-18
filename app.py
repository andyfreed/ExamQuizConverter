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

        # Detect encoding
        encoding = detect_encoding(bytes_data)

        # Decode the content with fallbacks
        if encoding:
            try:
                content = bytes_data.decode(encoding)
            except UnicodeDecodeError:
                # Try common encodings if detected encoding fails
                for enc in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        content = bytes_data.decode(enc)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise UnicodeDecodeError(f"Could not decode file with any common encoding")
        else:
            content = bytes_data.decode('utf-8')  # Fallback to UTF-8

        return content, None
    except Exception as e:
        return None, f"Error reading file: {str(e)}"

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

                # Preview the data
                st.subheader("Preview of Parsed Questions")
                st.dataframe(df)

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
                missing_answers = df[df[['A', 'B', 'C', 'D']].isna().any(axis=1)]
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
        1. Questions should start with a number or 'Q' followed by a number
        2. Answer choices should be labeled A, B, C, D
        3. Correct answer should be indicated with 'Correct Answer: X'

        ### Example Format:
        ```
        1. What is the present value of an annuity?
        A. The future value of all payments
        B. The sum of all payments
        C. The current worth of all future payments
        D. The average of all payments
        Correct Answer: C

        2. Which factor affects annuity calculations?
        A. Interest rate
        B. Payment frequency
        C. Time period
        D. All of the above
        Correct Answer: D
        ```
        """)

if __name__ == '__main__':
    main()