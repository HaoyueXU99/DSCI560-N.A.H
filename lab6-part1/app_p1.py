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


def get_pdf_text(pdf_docs):
    """
    Convert PDFs into Text document suitable for embeddings and GPT.
    """
    full_text = []
    for pdf_doc in pdf_docs:
        with open(pdf_doc, "rb") as file:
            pdf_reader = PyPDF2.PdfFileReader(file)
            for page_num in range(pdf_reader.numPages):
                page = pdf_reader.getPage(page_num)
                full_text.append(page.extractText())
    return "\n".join(full_text)


def get_text_chunks(text):
    """
    Split the text document into short, mostly self-contained sections to be embedded.
    """
    splitter = CharacterTextSplitter(max_length=500)
    return splitter.split(text)


def get_vectorstore(text_chunks):
    """
    Each section is embedded with the OpenAI API and embeddings are saved in a vector database.
    """
    embeddings = OpenAIEmbeddings()
    embedded_vectors = [embeddings.embed(chunk) for chunk in text_chunks]
    
    vector_store = FAISS()
    for vector in embedded_vectors:
        vector_store.add(vector)
    
    return vector_store


def get_conversation_chain(vectorstore):
    """
    Create a conversation chain to understand user questions and generate responses.
    """
    chat_model_openai = ChatOpenAI()
    memory_buffer = ConversationBufferMemory()

    conversation_chain = ConversationalRetrievalChain(
        model=chat_model_openai,
        memory=memory_buffer,
        vectorstore=vectorstore
    )
    
    return conversation_chain


def handle_userinput(user_question, conversation):
    """
    Handle user input and return GPT's answer.
    """
    embedded_query = OpenAIEmbeddings().embed(user_question)
    relevant_sections = conversation.vectorstore.rank(embedded_query)

    formatted_message = f"User: {user_question}\n" + "\n".join(relevant_sections)
    gpt_answer = conversation.ask(formatted_message)

    return gpt_answer


def main():
    pdf_docs = ['file1', 'file2']  # This should point to the actual file paths

    # Convert PDFs into text
    text = get_pdf_text(pdf_docs)

    # Split the text document into chunks
    text_chunks = get_text_chunks(text)

    # Embed the text chunks and save in a vector store
    vectorstore = get_vectorstore(text_chunks)

    # Create the conversation chain
    conversation = get_conversation_chain(vectorstore)

    # Get questions from the user and answer them
    while True:
        user_question = input("Please enter your question (type 'exit' to quit): ")
        if user_question.lower() == 'exit':
            break
        response = handle_userinput(user_question, conversation)
        print(f"Answer: {response}")

if __name__ == '__main__':
    main()
