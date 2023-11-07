import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from langchain import HuggingFacePipeline
from langchain.llms import LlamaCpp
import pandas as pd
import mysql.connector
import numpy as np

# from streamlit_login_auth_ui.widgets import __login__

#Change MySQL credentials
# HOSTNAME = "localhost"
# DATABASE = "Lab6_NAH"
# USERNAME = "root"
# PASSWORD = "Dsci560@1234"
# TABLE_NAME = "PDF_Text"


HOSTNAME = "localhost"
DATABASE = "Lab3_NAH"
USERNAME = "Dsci560"
PASSWORD = "Dsci560@1234"
TABLE_NAME = "PDF_Text"

# Function to extract text content from multiple PDFs.


def get_pdf_text(pdf_docs):
    texts = []
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        pages_text = [page.extract_text() for page in pdf_reader.pages]
        texts.extend(pages_text)
    return ''.join(texts)


# Function to split the extracted text into chunks.
def get_text_chunks(text):

    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=500,
        chunk_overlap=100,
        length_function=len
    )
    chunks = text_splitter.split_text(text)

    return chunks

def store_db(text_chunks):
    df = pd.DataFrame(text_chunks, columns=['text_chunk'])

    try:
        connection = mysql.connector.connect(
            host=HOSTNAME,
            user=USERNAME,
            password=PASSWORD,
        )
    except:
        return 0
    
    cursor = connection.cursor()
    connection.database = DATABASE
    
    cursor.execute("DROP TABLE IF EXISTS PDF_Text")
    create_table_query = """CREATE TABLE IF NOT EXISTS PDF_Text (Text_chunk text)"""
    cursor.execute(create_table_query)
    connection.commit()

    for i, row in df.iterrows():
        listt = list(row)
        result = tuple(listt)
        insert = "INSERT INTO PDF_Text values(%s)"
        cursor.execute(insert, tuple(result))

    # Commit the changes
    connection.commit()
    # Close the cursor and database connection
    cursor.close()
    connection.close()


# Function to create a vector store based on the text chunks using OpenAIEmbeddings.
def get_vectorstore(text_chunks):

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)

    return vectorstore

# Function to create a conversational retrieval chain to aid in the chat function.
def get_conversation_chain(vectorstore):

    # Initialize ChatOpenAI and ConversationBufferMemory
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

    # Setup retriever options
    retriever_options = {
        "search_type": "similarity",
        "search_kwargs": {"k": 4}
    }

    # Create the conversational retrieval chain

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(**retriever_options),
        memory=memory,
    )
    return conversation_chain

# # Function to handle the user input, get a response, and manage the chat history.
# def handle_userinput(user_question):

#     if not st.session_state.conversation or not callable(st.session_state.conversation):
#         st.session_state.show_warning = True
#         return
    
#     st.session_state.show_warning = False
    
#     # Get the response from the conversation chain.
#     response = st.session_state.conversation({'question': user_question})

#     # Append the chatbot's response to the chat history.
#     st.session_state.messages.append({"role": "assistant", "content": response['answer']})

#     # Display the chatbot's response.
#     with st.chat_message("assistant"):
#         st.write(response['answer'])


# Function to handle the user input, get a response, and manage the chat history.
def handle_userinput(user_question):

    # Check if the conversation has been initialized with PDF content
    if 'conversation' in st.session_state and st.session_state.conversation is not None:
        # Get the response from the conversation chain with PDF content.
        response = st.session_state.conversation({'question': user_question})
    else:
        # Initialize a direct GPT-3 conversation chain without PDF content.
        llm = ChatOpenAI()
        memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
        retriever = []
        direct_conversation_chain = ConversationalRetrievalChain.from_llm(llm=llm, memory=memory, retriever=retriever)
        response = direct_conversation_chain({'question': user_question})

    # Append the chatbot's response to the chat history.
    st.session_state.messages.append({"role": "assistant", "content": response['answer']})

    # Display the chatbot's response.
    with st.chat_message("assistant"):
        st.write(response['answer'])



# Function to clear the chat history
def clear_chat_history():

    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you with your documents?"}]

# Main function for the Streamlit app.
def main():
    # Load environment variables.
    load_dotenv()

    # Set the page configuration for the Streamlit app.
    st.set_page_config(page_title="Expedition Bot: Plan Your Next trip!",
                       page_icon=":rocket:",
                       layout="centered")
    
    st.write(css, unsafe_allow_html=True)


    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None


    st.header(":astronaut: Chat with Questy Now!")

    # Store conversation messages
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you with your documents?"}]

    # Display or clear chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])


    # User-provided prompt
    user_question = st.chat_input("Ask questions about your documents:")
    if user_question:
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.write(user_question)
        handle_userinput(user_question)


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
            "Choose how you'd like to upload PDFs:",
            ("Upload a single PDF", "Upload multiple PDFs")
        )
        
        # Step 2: Adjust the file_uploader based on the user's choice
        if upload_choice == "Upload a single PDF":
            pdf_docs = st.file_uploader(
                "Please submit your PDF before asking! 💬 ", key=st.session_state.upload_key, accept_multiple_files=False
            )
        else:
            pdf_docs = st.file_uploader(
                "Please submit your PDFs before asking! 💬 ", key=st.session_state.upload_key, accept_multiple_files=True
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

            if not st.session_state.get('uploaded_docs'):
                # If no PDF is uploaded, we initialize the direct conversation chain
                # without relying on the PDF content
                if 'conversation' not in st.session_state or st.session_state.conversation is None:
                    llm = ChatOpenAI()
                    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
                    retriever = []
                    st.session_state.conversation = ConversationalRetrievalChain.from_llm(llm=llm, memory=memory, retriever=retriever)
                st.warning("You can now chat directly without uploading a PDF.")
            
            else:

                with st.spinner("Processing"):
                    # Extract text from the PDFs.
                    if isinstance(pdf_docs, list):
                        raw_text = get_pdf_text(pdf_docs)
                    else:
                        raw_text = get_pdf_text([pdf_docs])


                    # Split the extracted text into chunks.
                    text_chunks = get_text_chunks(raw_text)

                    #store chunks to MySQL
                    store_db(text_chunks)

                    # Create a vector store based on the text chunks.
                    vectorstore = get_vectorstore(text_chunks)

                    # Initialize the conversational retrieval chain for the session.
                    st.session_state.conversation = get_conversation_chain(
                        vectorstore)
                    
                    st.success("Upload successfully!")              
                    


                
        st.subheader("About")
        st.markdown('This is the Lab6-part1 project developed by **@N.A.H**.')

        if st.session_state.get('show_warning', False):
            st.warning("Please submit a PDF before asking questions!")


# Entry point for the script. If this script is run as the main module, the main() function is executed.
if __name__ == '__main__':
    main()
