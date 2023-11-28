# chatbot.py

from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from scrapers import scrape_hotels, scrape_flights
from responses import get_cheapest_flights_response, get_hotels_response
from pdf_processing import extract_images_from_pdf
import streamlit as st
from utils import get_first_image_data
import openai


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



def get_intent(user_question):

    openai.api_key = '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'  # Replace with your actual OpenAI API key

    # Constructing the prompt
    prompt = f"Please determine the main intent of the following user query: '{user_question}'. The intent should be a single word or a short phrase."

    try:
        # Making a request to OpenAI
        response = openai.Completion.create(
          engine="davinci-002",  # Assuming GPT-4 is the latest; replace with the appropriate engine
          prompt=prompt,
          max_tokens=50  # Adjust as necessary
        )

        return response.choices[0].text.strip().lower()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to handle the user input, get a response, and manage the chat history.

def handle_userinput(user_question, pdf_docs):


    if 'flight_flag' not in st.session_state:
        st.session_state['flight_flag'] = False


    if 'hotel_flag' not in st.session_state:
        st.session_state['hotel_flag'] = False


    if user_question:

        intent = get_intent(user_question)
        print(f"Identified Intent: {intent}")

        if 'flight' in intent or 'flight' in user_question:

            if not st.session_state['flight_flag']:
                with st.chat_message("assistant"):
                    st.write("It looks like you want to check flight information. Please provide origin, destination and date.\
                            \n Example: Can you give me the best flights from LAX to JFK? I am planning to travel from 2023-12-01 to 2023-12-03.")

                st.session_state['flight_flag'] = True

            else:  
                flight_data, url = scrape_flights(user_question)

                response = get_cheapest_flights_response(flight_data, url)

                with st.chat_message("assistant"):
                    st.write(response)

                st.session_state.messages.append({"role": "assistant", "content": response})


        
        elif 'hotel' in intent or "hotel" in user_question:

            if not st.session_state['hotel_flag']:
                with st.chat_message("assistant"):
                    st.write("It looks like you want to check hotel information. Please provide the city, check-in and check-out dates.\
                            \n Example: Can you give me hotels to stay in New York? Check in is on 2023-12-01 and check out is 2023-12-07.")

                st.session_state['hotel_flag'] = True

            else:    
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
            # st.session_state.messages.append({"role": "assistant", "content": response['answer']})

            st.session_state.messages.append({"role": "assistant", "content": response})
            pdf_images = extract_images_from_pdf(st.session_state.uploaded_docs)


            with st.chat_message("assistant"):
                st.write(response['answer'])
                            # Display the chatbot's response.# THIS DISPLAYS IMAGE OF THE THE COVER OF THE PDF!!!!
            if pdf_images:
                for i in pdf_images:
                    st.image(i, caption='Extracted Image', use_column_width = True)
                    

    else:
        st.warning("Please provide a valid user question and submit a PDF before asking!")

