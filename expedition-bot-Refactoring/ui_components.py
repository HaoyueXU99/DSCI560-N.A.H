# ui_components.py
import streamlit as st


# Function to clear the chat history
def clear_chat_history():

    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you with your documents?"}]

# Custom Streamlit component to display images within the chat area
def image_in_chat(image_data, caption):
    image_str = f'<img src="data:image/png;base64,{image_data}" alt="{caption}">'
    st.markdown(image_str, unsafe_allow_html=True)


