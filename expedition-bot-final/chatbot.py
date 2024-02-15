"""
chatbot.py

This file contains the implementation of a chatbot for generating travel plans. 
The chatbot uses various modules and APIs to interact with the user and provide recommendations for daily activities, places to visit, and accommodations based on user preferences and input.

The main functions in this file include:
- get_conversation_chain: Creates a conversational retrieval chain to aid in the chat function.
- get_vectorstore: Creates a vector store based on text chunks using OpenAIEmbeddings.
- get_intent: Determines the main intent of a user question.
- create_travel_plan_prompt: Generates a prompt for the chatbot to generate a travel plan based on user input.
- query_gpt: Sends a prompt to the chatbot and returns the response.
- handle_userinput: Handles user input, gets a response from the chatbot, and manages the chat history.

The file also includes import statements for necessary modules and APIs, as well as helper functions for scraping data, processing PDFs, and other utility functions.
"""



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
import spacy
nlp = spacy.load('en_core_web_sm')

def get_conversation_chain(vectorstore, openai_api_key):

    # Function to create a conversational retrieval chain to aid in the chat function.

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


def get_vectorstore(text_chunks, openai_api_key):

    # Function to create a vector store based on the text chunks using OpenAIEmbeddings.

    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore



def get_intent(user_question):
    
    # This function should take in a user question and return the intent of the question.
    # For example, if the user question is "What is the weather like today?", the intent should be "weather".

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


def create_travel_plan_prompt(departure_date, return_date, trip_duration, preferred_time, 
                              destination, travel_companions, trip_purpose, activities_interest, 
                              accommodation_preferences, preferences):

    # This function should take in the user input and return a prompt for the chatbot to generate a travel plan.
    # The prompt should include the user input and some additional information to guide the chatbot to generate a travel plan.
    
    default_departure_date = "2024/01/01"
    default_return_date = "2024/01/08"
    default_trip_duration = "7 days"
    default_preferred_time = ["Morning"]
    default_destination = "New York"
    default_travel_companions = ["Friends"]
    default_trip_purpose = ["Leisure"]
    default_activities_interest = ["Sightseeing"]
    default_accommodation_preferences = ["Not specified"]

    departure_date = departure_date or default_departure_date
    return_date = return_date or default_return_date
    trip_duration = trip_duration or default_trip_duration
    preferred_time = preferred_time or default_preferred_time
    destination = destination or default_destination
    travel_companions = travel_companions or default_travel_companions
    trip_purpose = trip_purpose or default_trip_purpose
    activities_interest = activities_interest or default_activities_interest
    accommodation_preferences = accommodation_preferences or default_accommodation_preferences
    preferences = preferences or "No specific requirements or preferences."

    preferred_time_str = ", ".join(preferred_time)
    travel_companions_str = ", ".join(travel_companions)
    trip_purpose_str = ", ".join(trip_purpose)
    activities_interest_str = ", ".join(activities_interest)
    accommodation_preferences_str = ", ".join(accommodation_preferences)

    prompt = (
        "I need a comprehensive travel itinerary with suggestions for daily activities, places to visit, and any recommended accommodations. "
        "The plan should include specific names of local restaurants, boutiques, landmarks, and activities for each day. Include exact times, locations, and any relevant details for each activity. "
        "Here are the key details I've provided, but please feel free to suggest additional activities and options that you think would enhance the trip:\n"
        f"- Departure Date: {departure_date}\n"
        f"- Return Date: {return_date}\n"
        f"- Trip Duration: {trip_duration}\n"
        f"- Preferred Time of Departure and Return: {preferred_time_str}\n"
        f"- Destination: {destination}\n"
        f"- Travel Companions: {travel_companions_str}\n"
        f"- Purpose of Trip: {trip_purpose_str}\n"
        f"- Interests in Activities: {activities_interest_str}\n"
        f"- Accommodation Preferences: {accommodation_preferences_str}\n"
        f"- Specific Requirements or Preferences: {preferences}\n\n"
        "While the above details should be the focus, I'm also open to other unique and interesting suggestions that could make this trip more memorable. Please include a mix of activities, some directly aligned with the given preferences and others that are creative or unexpected, to provide a well-rounded travel experience."
        "The itinerary should be structured with clear headings for each day and bullet points for each activity, including recommendations for breakfast, lunch, and dinner spots, unique local attractions, and any evening entertainment."
        "The markdown format should be: #### Day 1 - Activity #### Day 2 -Activity, etc. "
        "Use some emojis at appropriate times."
    )

    return prompt


def query_gpt(prompt):

    # This function should take in a prompt and return a response from the chatbot.

    try:
        response = openai.Completion.create(
          engine="text-davinci-003",  
          prompt=prompt,
          max_tokens=3000,
          temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"An error occurred: {e}"


def handle_userinput(user_question, doc_flag):
    
    # Function to handle the user input, get a response, and manage the chat history.

    if 'flight_flag' not in st.session_state:
        st.session_state['flight_flag'] = False

    if 'hotel_flag' not in st.session_state:
        st.session_state['hotel_flag'] = False


    if user_question:

        # Append the user's question to the chat history.
        intent = get_intent(user_question)
        print(f"Identified Intent: {intent}")

        if 'flight' in intent or 'flight' in user_question:
            if not st.session_state['flight_flag']:
                
                # Get the departure and return dates from the user's previous input
                departure_date = st.session_state.get('departure_date')
                return_date = st.session_state.get('return_date')

                # If the user has provided both departure and return dates,
                # set the response to a message about checking flights
                if departure_date and return_date:
                    response = f"It looks like you want to check flight information. You previously mentioned planning to travel from {departure_date} to {return_date}. Please provide origin and destination, or specify different dates if needed.\n Please note that your format should be kept as: Can you give me the best flights from LAX to JFK? I am planning to travel from {departure_date} to {return_date}."
                # If the user has provided only one of departure or return dates,
                # set the response to a message about checking flights
                else:
                    response = "It looks like you want to check flight information. Please provide origin, destination and date. Example: Can you give me the best flights from LAX to JFK? I am planning to travel from 2023-12-01 to 2023-12-03."

                # Display the response to the user
                with st.chat_message("assistant"):
                    st.write(response)

                # Set the flag to true to indicate that the user has
                # requested to check flights
                st.session_state['flight_flag'] = True

            else:  
                # Scrape the flight data from the given URL
                flight_data, url = scrape_flights(user_question)
                # Get the cheapest flights from the user's input
                response = get_cheapest_flights_response(flight_data, url)

                # Display the response to the user
                with st.chat_message("assistant"):
                    st.write(response)

            # Append the response to the list of messages
            st.session_state.messages.append({"role": "assistant", "content": response})



        elif 'hotel' in intent or "hotel" in user_question:
            if not st.session_state['hotel_flag']:
                
                # Get the departure and return dates from the user
                departure_date = st.session_state.get('departure_date')
                return_date = st.session_state.get('return_date')

                # Check if the user has provided the departure and return dates
                if departure_date and return_date:
                    response = f"It looks like you want to check hotel information. You previously mentioned planning to stay from {departure_date} to {return_date}. Please provide the city name, or specify different check-in and check-out dates if needed.\n Please note that your format should be kept as: Can you give me hotels to stay in New York? Check in is on {departure_date} and check out is {return_date}."
                else:
                    response = "It looks like you want to check hotel information. Please provide the city, check-in and check-out dates. Example: Can you give me hotels to stay in New York? Check in is on 2023-12-01 and check out is 2023-12-07."

                # Send the response to the chat window
                with st.chat_message("assistant"):
                    st.write(response)

                # Set the hotel flag to true
                st.session_state['hotel_flag'] = True

            else:    
                # Scrape the hotel data from the user's question
                hotel_data, city, nights, url = scrape_hotels(user_question)
                # Get the response from the hotel data
                response = get_hotels_response(hotel_data, city, nights, url)  

                # Send the response to the chat window
                with st.chat_message("assistant"):
                    st.write(response)

            # Append the response to the messages list
            st.session_state.messages.append({"role": "assistant", "content": response})



        elif doc_flag == 1:
            if not st.session_state.conversation or not callable(st.session_state.conversation):
                st.session_state.show_warning = True
                return      

            st.session_state.show_warning = False

            # Get the response from the conversation chain.
            response = st.session_state.conversation({'question': user_question})

            # Append the chatbot's response to the chat history.
            st.session_state.messages.append({"role": "assistant", "content": response['answer']})

            # Extracting the city the user input
            doc = nlp(user_question)
            for entity in doc.ents:
                if entity.label_ == 'GPE':
                    city = entity.text    
            
            pdf_images = extract_images_from_pdf(st.session_state.uploaded_docs, city)

            with st.chat_message("assistant"):
                st.write(response['answer'])
                # Display the chatbot's response.
                if pdf_images:
                    for image in pdf_images:
                        col1, col2, col3 = st.columns([1, 2, 1]) 
                        with col2:  
                            st.image(image, use_column_width=True)

        else:

            response = query_gpt(user_question)

            # Display the chatbot's response.
            with st.chat_message("assistant"):
                st.write(response)

            st.session_state.messages.append({"role": "assistant", "content": response})
                    
    else:
        st.warning("Please provide a valid user question and submit a PDF for asking!")

