# scrapers.py
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# import time
# import pandas as pd
# import numpy as np
# import regex as re
# from bs4 import BeautifulSoup
# from datetime import datetime

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
import spacy
from datetime import datetime
nlp = spacy.load('en_core_web_sm')


import spacy
nlp = spacy.load('en_core_web_sm')

#Scrape hotel information from Booking.com website
def scrape_hotels(text):

    #Extract city and date information from question
    doc = nlp(text)
    try:
        for entity in doc.ents:
            if entity.label_ == 'GPE':
                city = entity.text
        dates = r"(\d+-\d+-\d+)"
        check_in = re.findall(dates, text.lower())[0]
        check_out = re.findall(dates, text.lower())[1]
    except:
        print("Failed to fetch hotels information. Please provide the city name and check-in/check-out dates")
        return 0

    # Calculate number of nights
    date_difference = datetime.strptime(check_out, '%Y-%m-%d') - datetime.strptime(check_in, '%Y-%m-%d')
    number_of_nights = date_difference.days

    #Construct the URL
    city = city.replace(' ','_')
    url = 'https://www.booking.com/searchresults.html?ss=' + city + '&ssne='+ city + '&ssne_untouched=' + city + '&checkin=' + check_in + '&checkout=' + check_out + '&nflt=ht_id%3D204'
    
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

    # Loop over the hotel elements and extract the desired data
    hotels = soup.findAll('div', {'data-testid': 'property-card'})
    hotels_data = []

    for hotel in hotels:
        name_element = hotel.find('div', {'data-testid': 'title'})
        name = name_element.text.strip()
        
        location_element = hotel.find('span', {'data-testid': 'address'})
        location = location_element.text.strip()
        
        price_element = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
        price = price_element.text.strip()
        price = int(price.replace('US$','').replace(',',''))
        
        review_element = hotel.find('div', {'class': 'a3b8729ab1 d86cee9b25'})
        try:
            rating = review_element.text.strip()
        except:
            rating = np.nan

        hotels_data.append({
            'name': name,
            'location': location,
            'price': price,
            'rating': rating
        })

    # Construct dataframe of results and sort by price and then rating
    hotels = pd.DataFrame(hotels_data)
    hotels.dropna(inplace=True)
    hotels_sorted = hotels.sort_values(by=['price', 'rating'], ascending=[True, False])

    return hotels_sorted, city, number_of_nights, url

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
