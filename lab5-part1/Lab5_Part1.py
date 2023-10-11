import os
import re
import glob
import time
import PyPDF2
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from collections import defaultdict
from selenium import webdriver
from pdf2image import convert_from_path
import pytesseract
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import mysql.connector

#HARD CODE STIMULATION PAGE NUMBER FOR EACH FILE
stimulation_page = {'W21796.pdf':19,'W22099.pdf':5,'W22220.pdf':15,'W22221.pdf':4,'W21266.pdf':19,'W20864.pdf':16,'W20863.pdf':15,'W20407.pdf':18,
                    'W20197.pdf':84,'W22247.pdf':47,'W22249.pdf':7,'W22731.pdf':8,'W22740.pdf':15,'W23230.pdf':5,'W23359.pdf':6,'W23360.pdf':5,
                    'W23361.pdf':6,'W23362.pdf':5,'W23363.pdf':6,'W23364.pdf':5,'W23365.pdf':6,'W23366.pdf':5,'W23367.pdf':9,'W23368.pdf':6,
                    'W23369.pdf':8,'W23370.pdf':5,'W23371.pdf':7,'W23372.pdf':6,'W25156.pdf':15,'W25157.pdf':9,'W25158.pdf':11,'W25159.pdf':8,
                    'W25160.pdf':9,'W25571.pdf':4,'W28190.pdf':4,'W28194.pdf':4,'W28303.pdf':6,'W28342.pdf':4,'W28394.pdf':6,'W28425.pdf':13,
                    'W28554.pdf':4,'W28557.pdf':11,'W28599.pdf':6,'W28600.pdf':7,'W28601.pdf':7,'W28633.pdf':7,'W28634.pdf':5,'W28636.pdf':5,
                    'W28648.pdf':6,'W28649.pdf':6,'W28651.pdf':5,'W28652.pdf':77,'W28654.pdf':8,'W28655.pdf':5,'W28658.pdf':3,'W28744.pdf':11,
                    'W28754.pdf':6,'W28755.pdf':6,'W28756.pdf':5,'W28976.pdf':6,'W28978.pdf':3,'W29242.pdf':5,'W29244.pdf':5,'W29316.pdf':5,
                    'W29317.pdf':7,'W29334.pdf':6,'W30188.pdf':22,'W30189.pdf':4,'W30789.pdf':5,'W36047.pdf':44,'W90244.pdf':11,'W90258.pdf':13,
                    'W90329.pdf':7}

# 3. Extract Information from PDF Files
# This function determines the pattern to extract the well name based on the given PDF filename.
def well_name_func(pdf):
    if pdf.split('/')[-1] == 'W23359.pdf':
        well_name_pattern = 'Well Name .+ \n(.*?)(?:\n|$)'
    elif pdf.split('/')[-1] == 'W28601.pdf':
        well_name_pattern = 'Well Name .+ \n(.*?)(?:\n|$|Before After)'
    elif pdf.split('/')[-1] in ['W20863.pdf','W22731.pdf','W20864.pdf','W20407.pdf']:
        well_name_pattern = 'Well or Facility Name : (.*?)(?:\n|$)'
    else:
        well_name_pattern = 'Well Name and Number \n(.*?)(?:\n|$)'
    return well_name_pattern

# This function determines the pattern to extract the API number based on the given PDF filename.
def api_func(pdf):
    if pdf.split('/')[-1] == 'W90258.pdf':
        API_pattern = '\d{2}\s?-\s?\d{3}\s?-\s?\d{5}'
    elif pdf.split('/')[-1] == 'W20407.pdf':
        API_pattern = '31-19H.*API\s(.*)'
    elif pdf.split('/')[-1] in ['W21796.pdf','W20863.pdf','W21266.pdf']:
        API_pattern = '\d{3}\s?-?\s?\d{5}'
    else:
        API_pattern = '\d{2}-\d{3}-\d{5}'
    return API_pattern

# This function fixes the API number format based on the given PDF filename and the matched API pattern.
def api_fix_func(pdf, API_pattern_match):
    if pdf.split('/')[-1] in ['W21796.pdf','W20863.pdf','W21266.pdf']:
        api_num = API_pattern_match.group(0)
        api_num_fixed = '33-'+api_num.split()[0]+'-'+api_num.split()[1]
    elif pdf.split('/')[-1] == 'W20407.pdf':
        api_num = API_pattern_match.group(1).strip()
        api_num_fixed = api_num[:2]+'-'+api_num[3:6]+'-'+api_num[6:]
    elif pdf.split('/')[-1] == 'W90258.pdf':
        api_num = API_pattern_match.group(0)
        api_num_fixed = api_num.replace(' ',"")
    else:
        api_num_fixed = API_pattern_match.group(0)
    return api_num_fixed

def extract_well_data_from_pdfs(folder_path):
    # Get a list of all PDF files in the given folder
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))

    # Create a dictionary to store extracted data from each PDF
    files_dict = defaultdict(dict)

    # Iterate over each PDF file
    for pdf in pdf_files:
        # Open the PDF file for reading
        pdf_file = open(pdf, "rb")
        # Initialize a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        # Get the number of pages in the PDF
        page_numbers = len(pdf_reader.pages)
        well_name_match = None
        API_pattern_match = None
        long_pattern_match = None
        lat_pattern_match = None
        # Iterate over each page in the PDF
        for page_num in range(page_numbers):
            try:
                # Get the text content of the page
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()

                # Get patterns to match well name and API number
                well_name_pattern = well_name_func(pdf)
                API_pattern = api_func(pdf)
                long_pattern = 'Longitude:(.*)(W|E)\s'
                lat_pattern = 'Latitude:(.*)(S|N)\s'

                if well_name_match is None:
                    well_name_match = re.search(well_name_pattern, page_text)
                    if well_name_match:
                        files_dict[pdf.split('/')[1]]['Well_name'] = well_name_match.group(1).strip()

                if API_pattern_match is None:
                    API_pattern_match = re.search(API_pattern, page_text)
                    if API_pattern_match:
                        api_num_fixed = api_fix_func(pdf, API_pattern_match)
                        files_dict[pdf.split('/')[1]]['API#'] = api_num_fixed.strip()               

                if long_pattern_match is None:
                    long_pattern_match = re.search(long_pattern, page_text)
                    if long_pattern_match:
                        files_dict[pdf.split('/')[1]]['Longitude'] = long_pattern_match.group(1).strip()

                if lat_pattern_match is None:
                    lat_pattern_match = re.search(lat_pattern, page_text)
                    if lat_pattern_match:
                        files_dict[pdf.split('/')[1]]['Latitude'] = lat_pattern_match.group(1).strip()

                if well_name_match and API_pattern_match and long_pattern_match and lat_pattern_match:
                    break
            except:
                # If there's any error in processing a page, move on to the next page
                continue
        print("Extract well data from pdfs:", files_dict[pdf.split('/')[1]])

    # Return the dictionary with extracted data from all PDFs
    return files_dict

# Extracts text from a specific page of a given PDF using OCR.
def extract_text_from_pdf(pdf_path, page_number):
    # Convert the specified PDF page to an image at 500 DPI
    pages = convert_from_path(pdf_path, 500, first_page=page_number, last_page=page_number)
    # Use pytesseract to extract text from the image
    text = pytesseract.image_to_string(pages[0])
    return text

# Extracts specific data from a given string based on patterns and positions.
def extract_row1_data(row1_string):

    # Remove any "|" characters from the string
    row1_string = row1_string.replace("|", "")

    # Split the string into a list of words
    row1_list = row1_string.split()

    # Initialize default values for extracted data
    date_stim, stim_form, top, bottom, stim_stages, volume, vol_units = [None]*7

    # Extract data based on conditions and positions
    if len(row1_list) >= 7:
        if re.match("^[a-zA-Z]+$", row1_list[0]) is None:
            date_stim = row1_list[0]
        stim_form = row1_list[1]
        if (stim_form == 'Three') or (stim_form == '3'):
            stim_form = 'Three Forks'
        if row1_list[2].isdigit():
            top = row1_list[-5]
        if row1_list[3].isdigit():
            bottom = row1_list[-4]
        if row1_list[4].isdigit():
            stim_stages = row1_list[-3]
        if row1_list[-2].isdigit():
            volume = row1_list[-2]
        if row1_list[-1] == 'Barrels':
            vol_units = row1_list[-1]

    return date_stim, stim_form, top, bottom, stim_stages, volume, vol_units

# Extracts type of treatment from the given string based on specific patterns.
def extract_type_treat_data(matched_string):
    type_treat = None
    if matched_string == 'Sand Frac':
        type_treat = matched_string
    elif 'Sand Frac' in matched_string:
        type_treat = 'Sand Frac'
    return type_treat

# Extracts data from a given row2_string based on specific patterns and positions.
def extract_row2_data(row2_string):

    # Remove any "|" characters from the string
    row2_string = row2_string.replace("|", "")

    # Split the string into a list of words
    row2_list = row2_string.split()

    # Initialize default values for extracted data
    acid, proppant, pressure, rate = [None]*4

    # Extract data based on conditions and positions
    if len(row2_list) >= 3:
        if len(row2_list) == 4:
            if row2_list[0].isdigit() and len(row2_list[0]) <= 3:
                acid = row2_list[0]
            elif row2_list[0].isdigit() and len(row2_list[0]) > 3:
                proppant = row2_list[0]
            else:
                if row2_list[-3].isdigit():
                    proppant = row2_list[-3]
                pressure = row2_list[-2]
                rate = row2_list[-1]
        else:
            proppant = row2_list[0]
            pressure = row2_list[1]
            rate = row2_list[2]

    return acid, proppant, pressure, rate

# Extracts details data based on specific conditions.
def extract_details_data(details):
    # Check specific conditions and return None if any of them are met
    if details.startswith('\nDate') or len(details) >= 500:
        return None
    return details

# Extracts stimulation data from a list of PDF files.
def extract_stimulation_data_from_pdfs(pdf_files):

    stimulation_dict = defaultdict(dict)

    # Iterate over each PDF file
    for pdf in pdf_files:
        pdf_file = open(pdf, "rb")
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Retrieve the page number for extraction from a predefined dictionary
        page_number = stimulation_page.get(pdf.split('/')[-1], None)

        date_stim, stim_form, top, bottom, stim_stages, volume, vol_units, type_treat, acid, proppant, pressure, rate, details= [None]*13

        # If a page number is found, extract data from it
        if page_number:
            text = extract_text_from_pdf(pdf, page_number)

            row1_sim_pattern = 'Units\n(.*)'
            type_treat_pattern = 'Min\)\n(\D*)'
            row2_sim_pattern = 'Min\)\n(.*)'
            details_sim_pattern = re.compile(r"Details\n(.*?).\n\nDa", re.DOTALL)

            row1_sim_pattern_match = re.search(row1_sim_pattern, text)
            type_treat_pattern_match = re.search(type_treat_pattern, text)
            row2_sim_pattern_match = re.search(row2_sim_pattern, text)
            details_sim_pattern_match = re.search(details_sim_pattern, text)

            if row1_sim_pattern_match:
                row1_string = row1_sim_pattern_match.group(1)
                # Extract row1 data from the text
                date_stim, stim_form, top, bottom, stim_stages, volume, vol_units = extract_row1_data(row1_string)

            if type_treat_pattern_match:
                matched_string = type_treat_pattern_match.group(1)
                # Extract type of treatment from the text
                type_treat = extract_type_treat_data(matched_string)

            if row2_sim_pattern_match:
                if type_treat is not None:
                    row2_string = row2_sim_pattern_match.group(1).replace(type_treat,"")
                # Extract row2 data from the text
                acid, proppant, pressure, rate = extract_row2_data(row2_string)

            if details_sim_pattern_match:
                # Extract additional details from the text
                details = details_sim_pattern_match.group(1)
                details = extract_details_data(details)

            # Populate the dictionary with extracted data
            stimulation_dict[pdf.split('/')[-1]] = {
                'Date_stimulated': date_stim,
                'Stim_formation': stim_form,
                'Top': top,
                'Bottom': bottom,
                'Stim_stages': stim_stages,
                'Volume': volume,
                'Units': vol_units,
                'Type_treatment': type_treat,
                'Acid%': acid,
                'Proppant_Lbs': proppant,
                'Max_Pressure': pressure,
                'Max_Rate': rate,
                'Details': details
            }

            print("extract stimulation data from pdfs:", stimulation_dict[pdf.split('/')[-1]])

        pdf_file.close()

    return stimulation_dict

# 4. Web Scraping Information
def scrape_well_data(df):

    # Initialize the Chrome WebDriver with options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
    chrome_options.add_argument('--no-sandbox')  # Disable sandboxing for Colab
    chrome_options.add_argument('--disable-dev-shm-usage')  # Disable shared memory usage

    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    well_status = []
    well_type = []
    closest_city = []

    for index, row in df.iterrows():
        well_name = row['Well_name'].strip()
        if 'see details' not in well_name:
            well_name_url = "-".join(well_name.replace('-'," ").split()).lower()
        else:
            well_name_url = 'none'
        try:
            api_num = row['API#'].strip()
        except:
            well_status.append('nan')
            well_type.append('nan')
            closest_city.append('nan')
            continue

        url = 'https://www.drillingedge.com/north-dakota/mckenzie-county/wells/'+well_name_url+"/"+api_num
        driver.get(url)
        time.sleep(1)

        # Get the page source after waiting
        page_source = driver.page_source

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Locate the table with the well information
        well_info_table = soup.find('table', {'class': 'skinny'})

        # Find all rows in the table
        try:
            rows = well_info_table.find_all('tr')

            for row in rows:
                header = row.find_all('th')
                data = row.find_all('td')
                for h, d in zip(header, data):
                    header_text = h.text.strip()
                    data_text = d.text.strip()
                    if header_text == 'Well Status':
                        well_status.append(data_text)
                    if header_text == 'Well Type':
                        well_type.append(data_text)
                    if header_text == 'Closest City':
                        closest_city.append(data_text)
            
        except:
            well_status.append('nan')
            well_type.append('nan')
            closest_city.append('nan')
            continue

    # Close the WebDriver when finished
    df['Well_status'] = well_status 
    df['Well_type'] = well_type 
    df['Closest_city'] = closest_city 

    driver.quit()

    return df

# Merge the data from two dictionaries into a single dataframe and save to a CSV.

def merge_and_save_dataframes(files_dict, stimulation_dict, output_folder):
    # Convert the dictionaries to dataframes
    df = pd.DataFrame.from_dict(files_dict,orient='index')
    df_stimulation = pd.DataFrame.from_dict(stimulation_dict,orient='index')

    # Merge the two dataframes on their indexes (horizontally)
    merged_df = pd.concat([df, df_stimulation], axis=1)
    print("Information Extracted from PDF: ", merged_df)

    # Save the merged dataframe to a CSV file
    merged_df.to_csv(output_folder + "Task_PDF_original.csv")

    return merged_df

def preprocess_and_save_dataframes(df, output_folder, task):

    if task == "a":
        # Remove HTML tags
        def remove_html_tags(text):
            clean = re.compile('<.*?>')
            return re.sub(clean, '', str(text))

        # Remove special characters (except for alphanumeric characters and spaces)
        def remove_special_characters(text):
            return re.sub('[^A-Za-z0-9\s\./-]+', '', str(text))

        processed_df = df.applymap(remove_html_tags)
        processed_df = processed_df.applymap(remove_special_characters)

        # Handle missing data
        # Replace NaN values in numeric columns with 0 and in string columns with "N/A"
        for column in processed_df.columns:
            if processed_df[column].dtype == 'object':  # If column is of object type, it's considered a string
                processed_df[column].fillna("N/A", inplace=True)
            else:  # If column is numeric
                processed_df[column].fillna(0, inplace=True)

        processed_df.replace("None", "nan", inplace=True)

        # Preprocess the "\n"
        processed_df.replace("\n", ";", regex=True, inplace=True)
        processed_df['Details'] = processed_df['Details'].str.replace(r"(;[\s;]+)", ";", regex=True).str.strip(";")

        # Save the merged dataframe to a CSV file
        processed_df.to_csv(output_folder+'Task1_PDF_preprocessed.csv', index=False)

    else:
        # Save the merged dataframe to a CSV file
        processed_df.to_csv(output_folder+'Task1_Web_preprocessed.csv', index=False)

        pass
    
    return processed_df

def store_db(df):
# Establishing a connection to the database
# Note: Change user name and password if needed
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Dsci560@1234',
        )
        # Create a cursor to interact with the database
        cursor = conn.cursor(buffered=True)
        # Ensure the database exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS Lab5_NAH")
        conn.database = 'Lab5_NAH'
        # Drop the table containing stock info if it exists
        cursor.execute("DROP TABLE IF EXISTS wells_data")
        # Create a table for raw stock data if it doesn't already exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS wells_data (
        Well_name text,
        API_number varchar(50),
        Longitude varchar(50),
        Latitude varchar(50),
        Date_stimulated varchar(50),
        Stimulation_formation varchar(50),
        Top varchar(50),
        Bottom varchar(50),
        Stimulation_stages varchar(50),
        Volume varchar(50),
        Units text,
        Type_Treatment text,
        Acid varchar(50),
        Proppant_Lbs varchar(50),
        Max_Pressure varchar(50),
        Max_Rate varchar(50),
        Details text,
        Well_staturs text,
        Well_type text,
        Closest_city text
        )
        """
        cursor.execute(create_table_query)
        # Committing any changes made during the initialization
        conn.commit()
        #Populating table
        for i, row in df.iterrows():
            listt = list(row)
            result = tuple(listt)
            insert = "INSERT INTO wells_data values(%s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(insert, tuple(result))
        # Commit the changes
        conn.commit()
        # Close the cursor and database connection
        cursor.close()
        conn.close()
    except:
        return None
    
# Running the code
if __name__ == "__main__":

    # Define the folder path containing the PDF files and retrieve the list of PDF files
    folder_path = 'DSCI560_Lab5'
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))

    # Extract well data and stimulation data from the PDFs
    files_dict = extract_well_data_from_pdfs(folder_path)
    stimulation_dict = extract_stimulation_data_from_pdfs(pdf_files)

    # Define the output folder path
    output_folder = ''

    # Merge the extracted data and save to a CSV
    merged_df = merge_and_save_dataframes(files_dict, stimulation_dict, output_folder)

    # preprocess the original data
    processed_df = preprocess_and_save_dataframes(merged_df, output_folder, "a")
    print(processed_df)

    # web scraping
    web_df = scrape_well_data(processed_df)
    print(web_df)

    # store final df
    store_db(web_df)