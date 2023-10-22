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
from streamlit_login_auth_ui.widgets import __login__

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

# Function to handle the user input, get a response, and manage the chat history.
def handle_userinput(user_question):

    if not st.session_state.conversation or not callable(st.session_state.conversation):
        st.session_state.show_warning = True
        return
    
    st.session_state.show_warning = False
    
    # Get the response from the conversation chain.
    response = st.session_state.conversation({'question': user_question})

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
    st.set_page_config(page_title="PDFs Masters",
                       page_icon=":mortar_board:",
                       layout="centered")
    
    st.markdown("""
    <style type="text/css">
    blockquote {
        margin: 1em 0px 1em -1px;
        padding: 0px 0px 0px 1.2em;
        font-size: 20px;
        border-left: 5px solid rgb(230, 234, 241);
        # background-color: rgb(129, 164, 182);
    }
    blockquote p {
        font-size: 30px;
        color: #FFFFFF;
    }
    [data-testid=stSidebar] {
        background-color: rgb(129, 164, 182) !important;
        color: #FFFFFF;
    }
    [aria-selected="true"] {
        color: #000000;
    }    
    button {
        color: rgb(129, 164, 182) !important;
    }
    ::placeholder {
        color: rgb(129, 164, 182) !important;
    }  
    input {
        color: #115675 !important;
                
    }
                                  
    </style>
    
    """, unsafe_allow_html=True)
    
    st.write(css, unsafe_allow_html=True)

    # __login__obj = __login__(auth_token="courier_auth_token", 
    #                     company_name="Shims",
    #                     width=200, height=250, 
    #                     logout_button_name='Logout', hide_menu_bool=False, 
    #                     hide_footer_bool=False, 
    #                     lottie_url='https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')


    # # Initialize a session state variable to track login status
    # if "is_logged_in" not in st.session_state:
    #     st.session_state.is_logged_in = False
    

    # Display the login UI if the user is not logged in
    # if not st.session_state.is_logged_in:

        # LOGGED_IN = __login__obj.build_login_ui()

        # if LOGGED_IN == True:
        #     st.session_state.is_logged_in = True
        #     st.markdown("Your Streamlit Application Begins here!")
        
    # else:
        # User is logged in, allow them to access the Chat with PDFs page

        # Initialize conversation and chat history in the session state if they don't exist.

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    # Main header for the app.
    # username= __login__obj.get_username()
    # st.header(username,":memo: Chat with your PDFs now!")

    st.header(":memo: Chat with your PDFs now!")

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

    # Sidebar for uploading PDF documents.
    with st.sidebar:
        st.title("Welcome to Chat with PDFs! :wave:")
        pdf_docs = st.file_uploader(
            "Please submit your PDF before asking! 💬 ", accept_multiple_files=True)
        if st.button("Submit"):
            with st.spinner("Processing"):
                # Extract text from the PDFs.
                raw_text = get_pdf_text(pdf_docs)

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
                
                if st.button('Clear Chat History', on_click=clear_chat_history, key='clear_button', help="Click to clear chat history"):
                    st.info("Chat history has been cleared.")

                
        st.subheader("About")
        st.markdown('This is the Lab6-part1 project developed by **@N.A.H**.')

        if st.session_state.get('show_warning', False):
            st.warning("Please submit a PDF before asking questions!")


# Entry point for the script. If this script is run as the main module, the main() function is executed.
if __name__ == '__main__':
    main()
