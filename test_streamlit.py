import streamlit as st

st.title("Test App")
st.write("If you can see this, Streamlit is working!")

# Add a button to confirm interactivity
if st.button("Click me"):
    st.success("Button clicked!") 