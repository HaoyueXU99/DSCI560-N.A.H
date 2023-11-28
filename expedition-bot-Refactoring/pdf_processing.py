# pdf_processing.py

from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter


def extract_images_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    page = reader.pages[16]  # You might need to adjust the page index
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
