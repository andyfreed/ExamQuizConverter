import streamlit as st
from apps.question_converter import main as question_converter_app

# Set page config at the very beginning
st.set_page_config(
    page_title="Question Converter Tool",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dictionary of available apps
APPS = {
    "Question Converter": question_converter_app,
}

def main():
    st.sidebar.title("Navigation")
    
    # App selection
    app_name = st.sidebar.selectbox(
        "Choose an application",
        list(APPS.keys())
    )
    
    # Run the selected app
    APPS[app_name]()

if __name__ == "__main__":
    main() 