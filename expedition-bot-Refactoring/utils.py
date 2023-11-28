# utils.py
from PyPDF2 import PdfReader

# This file can include smaller helper functions that don't fit into the other categories.
# For example, formatting functions, small data processing tasks, etc.
def get_first_image_data(pdf_docs):
    if pdf_docs:
        first_pdf = pdf_docs[0] if isinstance(pdf_docs, list) else pdf_docs
        first_pdf_reader = PdfReader(first_pdf)
        first_page_images = first_pdf_reader.pages[0].images
        if first_page_images:
            return first_page_images[0].data
    return None