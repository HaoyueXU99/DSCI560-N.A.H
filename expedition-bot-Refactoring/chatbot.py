# chatbot.py

from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from scrapers import scrape_hotels, scrape_flights
from responses import get_cheapest_flights_response, get_hotels_response
import streamlit as st
from utils import get_first_image_data



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


# Function to create a vector store based on the text chunks using OpenAIEmbeddings.
def get_vectorstore(text_chunks, openai_api_key):
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


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
        
        if 'hotel' in user_question.lower():
            hotel_data, city, nights, url = scrape_hotels(user_question)
            response = get_hotels_response(hotel_data, city, nights, url)

            # Append the chatbot's response to the chat history.
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Display the chatbot's response.
            with st.chat_message("assistant"):
                st.write(response)
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
