# main.py
import streamlit as st
from pdf_processing import extract_images_from_pdf, get_page_number, get_pdf_text, get_text_chunks
from chatbot import handle_userinput, get_conversation_chain, get_vectorstore
from ui_components import clear_chat_history,image_in_chat
from utils import get_first_image_data
from responses import get_cheapest_flights_response, get_hotels_response
from config import initialize_config
import streamlit as st
from htmlTemplates import css
import numpy as np
import spacy
nlp = spacy.load('en_core_web_sm')


def main():

    initialize_config()

    # Set the page configuration for the Streamlit app.
    st.set_page_config(page_title="Expedition Bot: Plan Your Next trip!",
                       page_icon=":rocket:",
                       layout="centered")
    
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header(":astronaut: Chat with Expedition Bot Now!")

    # Store conversation messages
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you with your trip?"}]

    # Display or clear chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User-provided prompt
    user_question = st.chat_input("Ask questions about your trip:")

    if user_question:
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.write(user_question)

        if not st.session_state.get('uploaded_docs'):
            st.warning("Please submit a PDF before asking questions!")
            st.session_state.show_warning = True
        else:
            st.session_state.show_warning = False
            st.success("Question received!")
            st.success("Handling user input...") 
            handle_userinput(user_question, st.session_state.uploaded_docs)

    else:
        st.session_state.show_warning = False

    if st.button('Clear Chat History', on_click=clear_chat_history, key='clear_button', help="Click to clear chat history"):
        st.info("Chat history has been cleared.")

    # Sidebar for uploading PDF documents.
    with st.sidebar:
        st.title("Welcome Adventurer! :wave:")

        # If 'upload_key' is not in session_state, initialize it with a random value
        if 'upload_key' not in st.session_state:
            st.session_state.upload_key = str(np.random.randint(0, 1000000))

        # Step 1: Add a radio button for user choice
        upload_choice = st.radio(
            "Do you have a travel guide? You can upload one to ask! \n Choose how you'd like to upload PDFs:",
            ("Upload a single PDF", "Upload multiple PDFs")
        )
        
        # Step 2: Adjust the file_uploader based on the user's choice
        if upload_choice == "Upload a single PDF":
            pdf_docs = st.file_uploader(
                "Please submit your travel guide before asking! 💬 ", key=st.session_state.upload_key, accept_multiple_files=False
            )
        else:
            pdf_docs = st.file_uploader(
                "Please submit your travel guides before asking! 💬 ", key=st.session_state.upload_key, accept_multiple_files=True
            )
            
                # Store the uploaded documents in session state
        if pdf_docs:
            st.session_state.uploaded_docs = pdf_docs

    # Button to delete the current documents
        if st.button('Delete Current Document(s)'):
            if 'uploaded_docs' in st.session_state:
                del st.session_state.uploaded_docs  # Delete the uploaded documents from the session state
                st.session_state.deleted = True  # Set the deleted state to True
                # Change the 'upload_key' to reset the file uploader
                st.session_state.upload_key = str(np.random.randint(0, 1000000))
                st.experimental_rerun()  # Rerun the app

        if st.session_state.get('deleted', False):
            st.warning("The uploaded document(s) have been deleted!")
            st.session_state.deleted = False  # Reset the deleted state after showing the message

        if st.button("Submit"):
            if not st.session_state.uploaded_docs:
                st.warning("Please submit a PDF before asking!")
            else:

                with st.spinner("Processing"):
                    # Extract text from the PDFs.
                    if isinstance(pdf_docs, list):
                        raw_text = get_pdf_text(pdf_docs)
                    else:
                        raw_text = get_pdf_text([pdf_docs])

                    # Split the extracted text into chunks.
                    text_chunks = get_text_chunks(raw_text)

                    #Open API Key
                    api_key = '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'

                    # Create a vector store based on the text chunks.
                    vectorstore = get_vectorstore(text_chunks, api_key)

                    # Initialize the conversational retrieval chain for the session.
                    st.session_state.conversation = get_conversation_chain(
                        vectorstore, api_key)

                        # Extract images from the uploaded PDF
                    # pdf_images = extract_images_from_pdf(st.session_state.uploaded_docs)

                    # # Display the first image (you might need to adjust this based on your use case)
                    # if pdf_images:
                    #     st.image(pdf_images[0], caption='Extracted Image', use_column_width=True)

                    # handle_userinput(user_question, pdf_docs)

                        
                    st.success("Upload successfully!")              
                    
        st.subheader("About")
        st.markdown('This project is developed by team **@N.A.H**.')

        if st.session_state.get('show_warning', False):
            st.warning("Please submit a PDF before asking questions!")

if __name__ == '__main__':
    main()
