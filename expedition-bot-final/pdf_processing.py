'''
pdf_processing.py

- function called extract_images_from_pdf that extracts images from a PDF file. 
    The function takes a list of PDF files and the name of a city as input parameters. 
    It searches for the specified city in each PDF file and identifies the page with the most mentions of the city. 
    Then, it extracts the images from that page and returns them as a list.

- Function to extract text content from multiple PDFs.
- Function to split the extracted text into chunks.
'''


from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter


def extract_images_from_pdf(pdf_files, city):
    '''
    Extracts images from a PDF file.
    
    Parameters:
    pdf_files (list): List of PDF files.
    city (str): Name of the city to search for.
    
    Returns:
    list: List of images from the PDF file.
    '''
    max_mentions = 0
    most_mentioned_page = None
    selected_pdf = None
    for pdf in pdf_files:
        page_num = 0
        try: 
            len(pdf_files)
        except:
            pdf = pdf_files
        reader = PdfReader(pdf)
        for page in reader.pages:
            pages_text = page.extract_text()
            mentions = pages_text.lower().count(city.lower())
            if mentions > max_mentions:
                max_mentions = mentions
                most_mentioned_page = page_num
                selected_pdf = pdf
            page_num+=1
        if isinstance(pdf_files, list):
            continue
        else:
            break
    reader = PdfReader(selected_pdf)
    page = reader.pages[most_mentioned_page]  # You might need to adjust the page index
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
