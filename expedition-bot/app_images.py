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
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import regex as re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

#Scrape flight information from Kayak website
def scrape_flights(text):
    
    #Regex patterns to extract information from question
    origin_pattern = r"from (\w{3})\W"
    destination_pattern = r"to (\w{3})\W"
    startdate_pattern = r"from (\d+-\d+-\d+)"
    enddate_pattern = r"to (\d+-\d+-\d+)"
    try:
        origin = re.findall(origin_pattern, text.lower())[0]
        destination = re.findall(destination_pattern, text.lower())[0]
        startdate = re.findall(startdate_pattern, text.lower())[0]
        enddate = re.findall(enddate_pattern, text.lower())[0]
    except:
        print("Failed to fetch flight information from Kayak. Please enter the information in the correct format")
        return 0
    
    #Construct the URL
    url = "https://www.kayak.com/flights/" + origin + "-" + destination + "/" + startdate + "/" + enddate + "?sort=price_a&fs=stops=0"

    #Starting Chromedriver, getting the URL, and scraping
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
    chrome_options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url) 
    time.sleep(20)
    soup=BeautifulSoup(driver.page_source, 'html.parser')
        
    #Extract flight times
    times = soup.find_all('div', attrs={'class': 'vmXl vmXl-mod-variant-large'})
    dep_time_1 = [] #Heading departure time
    dep_time_2 = [] #Return departure time

    arr_time_1 = [] #Heading arrival time
    arr_time_2 = [] #Return arrival time

    n = 0
    for flight_time in times:
        text = flight_time.getText()
        time_pattern = r'\d{1,2}:\d{2} [ap]m'
        dep = re.findall(time_pattern, text)[0]
        arr = re.findall(time_pattern, text)[1]
        if n%2 == 0:
            dep_time_1.append(dep)
            arr_time_1.append(arr)
        else:
            dep_time_2.append(dep)
            arr_time_2.append(arr)   
        n+=1
    
    #Extracting price information        
    price_elements = soup.find_all('div', class_='f8F1-price-text')
    valid_prices = []

    # Iterate through the price elements
    for price_element in price_elements:
        # Extract the parent element of the price element
        parent_element = price_element.find_parent().find_parent().find_parent().find_parent().find_parent().find_parent()
        # Check if the parent element contains "Basic"
        if parent_element and "Basic" in parent_element.get_text():
            valid_prices.append(price_element.get_text())
            continue
            
    #Extracting airline information
    airlines = soup.find_all('div', attrs={'class': 'c_cgF c_cgF-mod-variant-default','dir':'auto'})
    dep_airline = []
    return_airline = []
    n = 0
    for airline in airlines:
        if n%2 == 0:
            dep_airline.append(airline.getText())
        else:
            return_airline.append(airline.getText())
        n+=1
        
    #Constructing dataframe of results
    df = pd.DataFrame({"origin" : origin,
                       "destination" : destination,
                       "startdate" : startdate,
                       "enddate" : enddate,
                       "departure_airline": dep_airline,
                       "deptime_o": dep_time_1,
                       "arrtime_d": arr_time_1,
                       "return_airline": return_airline,
                       "deptime_d": dep_time_2,
                       "arrtime_o": arr_time_2,
                       "price": valid_prices
                       })
    
    return df, url

#Generate a text response for the cheapest flights.
def get_cheapest_flights_response(flight_data, url, num_flights=5):
    # Sort the DataFrame by the 'Price' column in ascending order to get the cheapest flights.
    cheapest_flights = flight_data.sort_values(by='price').head(num_flights)

    # Generate a text response based on the cheapest flights.
    response = f"Here are the top {num_flights} cheapest flights from {flight_data['origin'][0].upper()} to {flight_data['destination'][0].upper()}:\n"
    
    for idx, row in cheapest_flights.iterrows():
        response += f"{idx + 1}. For {row['price']}, departure airline {row['departure_airline']}, departure time {row['deptime_o']}, arrival time {row['arrtime_d']}. Return airline {row['return_airline']}, departure time {row['deptime_d']}, arrival time  {row['arrtime_o']}\n"
    
    response += f"\nTo book your flight, visit {url}"
    
    return response

def extract_images_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    page = reader.pages[0]  # You might need to adjust the page index
    count = 0
    images = []

    for image_file_object in page.images:
        images.append(image_file_object.data)

    return images

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

# Function to create a vector store based on the text chunks using OpenAIEmbeddings.
def get_vectorstore(text_chunks, openai_api_key):
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

# Function to create a conversational retrieval chain to aid in the chat function.
def get_conversation_chain(vectorstore, openai_api_key):
    llm = ChatOpenAI(openai_api_key=openai_api_key)
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 4}),
        memory=memory,
    )
    return conversation_chain

# Function to handle the user input, get a response, and manage the chat history.

def handle_userinput(user_question, pdf_docs):
    if user_question:
        if 'flight' in user_question.lower():
            flight_data, url = scrape_flights(user_question)
            response = get_cheapest_flights_response(flight_data, url)

            # Append the chatbot's response to the chat history.
            st.session_state.messages.append({"role": "assistant", "content": response, "image_data": get_first_image_data(pdf_docs)})

            # Display the chatbot's response.
            with st.chat_message("assistant"):
                st.write(response)

            # Display the image using HTML
            first_image_data = get_first_image_data(pdf_docs)
            if first_image_data:
                st.write(f'<img src="data:image/png;base64,{first_image_data}" alt="Image" width="200">')
        else:
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

    else:
        st.warning("Please provide a valid user question and submit a PDF before asking!")

import base64
def get_first_image_data(pdf_docs):
    if pdf_docs:
        first_pdf = pdf_docs[0] if isinstance(pdf_docs, list) else pdf_docs
        first_pdf_reader = PdfReader(first_pdf)
        first_page_images = first_pdf_reader.pages[0].images
        if first_page_images:
            return first_page_images[0].data
    return None



# Custom Streamlit component to display images within the chat area
def image_in_chat(image_data, caption):
    image_str = f'<img src="data:image/png;base64,{image_data}" alt="{caption}">'
    st.markdown(image_str, unsafe_allow_html=True)


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

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

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
        st.title("Welcome to Chat with PDFs! :wave:")

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
                    pdf_images = extract_images_from_pdf(st.session_state.uploaded_docs)

                    # Display the first image (you might need to adjust this based on your use case)
                    if pdf_images:
                        st.image(pdf_images[0], caption='Extracted Image', use_column_width=True)

                    # handle_userinput(user_question, pdf_docs)

                        
                    st.success("Upload successfully!")              
                    
        st.subheader("About")
        st.markdown('This project is developed by team **@N.A.H**.')

        if st.session_state.get('show_warning', False):
            st.warning("Please submit a PDF before asking questions!")

# Entry point for the script. If this script is run as the main module, the main() function is executed.
if __name__ == '__main__':
    main()