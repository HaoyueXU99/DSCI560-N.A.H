"""
main.py 

This file contains the main code for the Expedition Bot - Your Custom Travel Planner application.
It imports necessary modules and defines functions for rendering the form page and result page.
The form page allows users to input their travel preferences, while the result page displays the chat interface with the bot.
The code handles user input, processes the form data, and generates travel plans based on the user's preferences.
"""

import streamlit as st
from pdf_processing import extract_images_from_pdf, get_pdf_text, get_text_chunks
from chatbot import handle_userinput, get_conversation_chain, get_vectorstore, query_gpt, create_travel_plan_prompt
from ui_components import clear_chat_history,image_in_chat
from utils import get_first_image_data
from responses import get_cheapest_flights_response, get_hotels_response
from config import initialize_config
import streamlit as st
from htmlTemplates import css
import numpy as np
import spacy
nlp = spacy.load('en_core_web_sm')



def render_form_page():
    """
    Renders the form page for the Expedition Bot app.
    Allows users to input their travel preferences and submit the form.
    """

    # Set the page configuration for the Streamlit app.
    st.set_page_config(page_title="Welcome to Expedition Bot - Your Custom Travel Planner",
                        page_icon=":airplane:",
                        layout="centered")
    
    # Create a form with two buttons, submit and skip
    with st.form(key='my_form'):
        # Display a welcome message
        st.markdown("## ✈️ Welcome to Expedition Bot ")
        st.markdown("### 🧑🏻‍✈️ Your Custom Travel Planner")
        st.markdown("Let's embark on a journey to create your perfect getaway. Just a few quick questions and you'll be on your way to an unforgettable adventure! 🌍")


        # Display a message to skip the form
        st.markdown("***_Feeling tired of answering questions? Don't worry, just click `Skip and Chat with Bot` and interact directly with our robot._***")
        
        # Create a submit button to skip the form
        skip_button = st.form_submit_button("Skip and Chat with Bot")

        # Display a message to start the form
        st.markdown("#### Let's start with when and where you want to explore.")
        st.caption("Your dream destination is just a few clicks away!")
        # Create a dropdown to select the departure date
        departure_date = st.date_input("Choose your potential Departure Date 🛫️")
        # Create a dropdown to select the return date
        return_date = st.date_input("Choose your potential Return Date 🛬️")
        # Create a dropdown to select the trip duration
        trip_duration = st.radio("Estimated Duration of Trip 🕐", 
                                 ["1-3 days", "4-7 days", "1-2 weeks", "2-3 weeks", "More than 3 weeks"])
        # Create a multiselect to select the preferred time of departure and return
        preferred_time = st.multiselect("Preferred Time of Departure and Return 🌞", 
                                        ["Early Morning", "Morning", "Afternoon", "Evening", "Night"])
        # Create a text area to enter the destination
        destination = st.text_area("Where would you like to travel? 🌍")
        


        # Display a message to start the form
        st.text("")  
        st.markdown("#### Who's joining you on this amazing journey?")

        # Display a message to select the travel companions
        st.caption("Select who will share these memorable moments with you.")

        # Create a multiselect to select the travel companions
        travel_companions = st.multiselect("Who will you be traveling with? (Select all that apply) 👨‍👩‍👧‍👦", 
                                           ["Family", "Friends", "Partner/Spouse", "Children", 
                                            "Alone", "Business Colleagues", "Others (Please specify in the end)"])

        # Display a message to start the form
        st.text("") 
        st.markdown("#### What's the flavor of your adventure?")
 
        # Display a message to select the trip purpose
        st.caption("Choose the experiences that make your heart race.")
        trip_purpose = st.multiselect("Purpose of the Trip (Select all that apply) 🏝️",
                                      ["Leisure", "Adventure", "Cultural Experience", "Business", 
                                       "Relaxation", "Visiting Friends/Family", "Other (Please specify in the end)"])
        

        # Create a multiselect to select the activities interest
        activities_interest = st.multiselect("Preferences for Activities (Select all that apply) 🏄",
                                             ["Hiking", "Sightseeing", "Culinary Exploration", "Beach Activities",
                                              "Skiing/Snowboarding", "Historical Tours", "Wildlife and Nature",
                                              "Shopping", "Arts and Museums", "Sports and Outdoor Activities",
                                              "Nightlife and Entertainment", "Other (Please specify in the end)"])
        
        # Display a message to start the form
        st.text("")  
        st.markdown("#### Let's find you the perfect place to stay.")
        st.caption("Cozy, luxurious, or unique – what's your style?")
        # Create a multiselect to select the accommodation preferences
        accommodation_preferences = st.multiselect("Accommodation Preferences (Select all that apply) 🏨",
                                                   ["Hotel (Specify star rating: )", "Hostel", "Bed and Breakfast",
                                                    "Apartment Rental", "Luxury Resort", "Eco-Friendly Options",
                                                    "Location Preference (Specify: )", "Budget-Friendly", 
                                                    "Family-Friendly", "Romantic/Secluded", "Other (Please specify in the end)"])
        # Display a message to start the form
        st.text("")  
        st.markdown("#### Almost there! A few last details to tailor your experience.")
        st.caption("Your preferences matter. Let's make this trip fit your budget and needs.")
        # Create a text area to enter the preferences
        preferences = st.text_area("Any specific requirements or preferences? 📝️")

        # Create a submit button to submit the form
        submit_button = st.form_submit_button("Submit")

        # Check if the submit button is clicked
        if submit_button:
            # Set the page to result
            st.session_state['page'] = 'result'
            # Store form data in session state or process as needed
            st.session_state['form_filled'] = True
            # Store the departure date in session state
            st.session_state['departure_date'] = departure_date
            # Store the return date in session state
            st.session_state['return_date'] = return_date
            # Store the trip duration in session state
            st.session_state['trip_duration'] = trip_duration
            # Store the preferred time in session state
            st.session_state['preferred_time'] = preferred_time
            # Store the destination in session state
            st.session_state['destination'] = destination
            # Store the preferences in session state
            st.session_state['preferences'] = preferences
            # Store the travel companions in session state
            st.session_state['travel_companions'] = travel_companions
            # Store the trip purpose in session state
            st.session_state['trip_purpose'] = trip_purpose
            # Store the activities interest in session state
            st.session_state['activities_interest'] = activities_interest
            # Store the accommodation preferences in session state
            st.session_state['accommodation_preferences'] = accommodation_preferences

        # Check if the skip button is clicked
        elif skip_button:
            # Set the page to result
            st.session_state['page'] = 'result'
            # Set the form filled status to false
            st.session_state['form_filled'] = False
            st.session_state['page'] = 'result'
            st.session_state['form_filled'] = False


def render_result_page():

    initialize_config()

    # Set the page configuration for the Streamlit app.
    st.set_page_config(page_title="Expedition Bot: Plan Your Next trip!",
                       page_icon=":airplane:",
                       layout="centered")
    
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("🧑🏻‍✈️ Chat with Expedition Bot Now!")

    # Store conversation messages

    if "messages" not in st.session_state.keys():
        # Initialize the messages list
        
        if st.session_state.get('form_filled', False):
            # if the user has filled the form, show the travel plan 
            prompt = create_travel_plan_prompt(
                st.session_state.get('departure_date'),
                st.session_state.get('return_date'),
                st.session_state.get('trip_duration'),
                st.session_state.get('preferred_time', []),
                st.session_state.get('destination', "Not specified"),
                st.session_state.get('travel_companions', []),
                st.session_state.get('trip_purpose', []),
                st.session_state.get('activities_interest', []),
                st.session_state.get('accommodation_preferences', []),
                st.session_state.get('preferences', "No specific requirements.")
            )
            response = "Based on your input, here is a possible travel itinerary for your reference:\n"
            response += query_gpt(prompt)
            st.session_state.messages = [{"role": "assistant", "content": response}]
        else:
            # if the user has not filled the form, show a welcome message
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
            # st.warning("Please submit a PDF before asking questions!")
            # st.session_state.show_warning = True
            handle_userinput(user_question, doc_flag=0)
            st.success("Question received! ")

        else:
            st.session_state.show_warning = False
            st.success("Question received!")
            st.success("Handling user input with uploaded PDFs...") 
            handle_userinput(user_question, doc_flag=1)




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
                "Please submit your travel guide for asking! 💬 ", key=st.session_state.upload_key, accept_multiple_files=False
            )
        else:
            pdf_docs = st.file_uploader(
                "Please submit your travel guides for asking! 💬 ", key=st.session_state.upload_key, accept_multiple_files=True
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

        # if st.session_state.get('show_warning', False):
        #     st.warning("Please submit a PDF before asking questions!")

def main():

    # Set the page to the default page if it is not already set
    if 'page' not in st.session_state:
        st.session_state['page'] = 'form'

    # If the page is the form page, render the form page
    if st.session_state['page'] == 'form':
        render_form_page()
    # If the page is the result page, render the result page
    elif st.session_state['page'] == 'result':
        render_result_page()
if __name__ == '__main__':
    main()
