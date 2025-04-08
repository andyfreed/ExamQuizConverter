import streamlit as st
import os
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
    # Configure Streamlit for Azure environment
    if os.environ.get('WEBSITE_HOSTNAME'):  # Check if running on Azure
        st.set_option('server.address', '0.0.0.0')
        st.set_option('server.port', int(os.environ.get('PORT', 8000)))
        st.set_option('server.baseUrlPath', '')
    
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