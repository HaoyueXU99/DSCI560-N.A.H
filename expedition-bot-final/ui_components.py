# ui_components.py

'''
ui_components.py 

This file focuses on chat interface enhancements. 

- Function, clear_chat_history to reset the chat history to an initial message from the assistant. 
- Function, image_in_chat, is a custom Streamlit component that allows for the display of images within the chat area, 
    with the image data and caption being passed as parameters. 
    This function uses HTML formatting to embed images directly into the Streamlit markdown,
    enhancing the interactivity of the chat interface.

'''
import streamlit as st


# Function to clear the chat history
def clear_chat_history():

    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you with your documents?"}]

# Custom Streamlit component to display images within the chat area
def image_in_chat(image_data, caption):
    image_str = f'<img src="data:image/png;base64,{image_data}" alt="{caption}">'
    st.markdown(image_str, unsafe_allow_html=True)


