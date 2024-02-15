# PDFs Masters - Chat with your PDFs!

The application provides a chat interface, allowing users to ask questions about the content of their uploaded PDFs. With the help of various libraries, the app extracts text from PDFs, chunks the data, and utilizes embeddings and vector stores to support a conversational experience with the content.

## Key Features

1. **PDF Upload**: Users can either upload a single PDF or multiple PDFs to chat about.
2. **MySQL Storage**: Extracted text chunks from PDFs are stored in a MySQL database.
3. **Vector Store Creation**: Text chunks are transformed into vector representations using HuggingFace's sentence-transformers.
4. **Conversational Retrieval Chain**: Combines embeddings, vector stores, and language models to facilitate a chat-like interaction with the PDF content.
5. **Dynamic Chat Interface**: Uses Streamlit's chat interface to create a conversational experience.
6. **Custom Styling**: Provides a custom look and feel for the application.

## Key Libraries and Modules Used:

- `streamlit`: For creating the web-based interactive app.
- `dotenv`: Load environment variables.
- `PyPDF2`: Extract text content from PDFs.
- `langchain`: A suite of utilities to handle text splitting, embeddings, vector stores, chat models, memory, and more.
- `htmlTemplates`: Custom HTML templates for chat aesthetics.
- `pandas`: Handle and manipulate data.
- `mysql.connector`: Connect to and interact with MySQL databases.
- `numpy`: Numerical computations.
- `transformers`: Access pre-trained transformer models from HuggingFace.

## Main Functions:

1. `get_pdf_text(pdf_docs)`: Extracts text content from a list of PDFs.
2. `get_text_chunks(text)`: Splits the given text into chunks based on specified criteria.
3. `store_db(text_chunks)`: Stores the provided text chunks in a MySQL database.
4. `get_vectorstore(text_chunks)`: Creates a vector store from text chunks using embeddings.
5. `get_conversation_chain(vectorstore)`: Sets up a conversational retrieval chain for the chat function.
6. `handle_userinput(user_question)`: Handles the user's questions, retrieves responses, and manages the chat history.
7. `clear_chat_history()`: Clears the chat history.
8. `main()`: The core function to set up and run the Streamlit app.

## Here is the difference we make

- Database Integration: MySQL is incorporated to store text chunks extracted from PDFs.


- User Interface: The application boasts an enhanced UI design using advanced CSS stylings, distinct from the reference code which employs basic styles.

- Chat Interface: My code uses native Streamlit chat UI functionalities while the reference code leans on custom HTML templates.


- Open source models (form Hugging Face) are used:
  - For embeddings: “all-MiniLM-L6-v2” sentence transformer
  - For text generation: “gpt2” language model



> The following content comes from the ReadMe file provided by the teacher。



## How it works

1. The application gui is built using streamlit
2. The application reads text from PDF files, splits it into chunks
3. Uses OpenAI Embedding API to generate embedding vectors used to find the most relevant content to a user's question 
4. Build a conversational retrieval chain using Langchain
5. Use OpenAI GPT API to generate respond based on content in PDF



## Requirements

1. Install the following Python packages:
```
pip install streamlit pypdf2 langchain python-dotenv faiss-cpu openai sentence_transformers
```

2. Create a `.env` file in the root directory of the project and add the following environment variables:
```
OPENAI_API_KEY= # Your OpenAI API key
```

3.  Create a folder named `.streamlit`  in your root:




4. In `.streamlit `, create `config.toml`:

```
[theme]
primaryColor="#29b5e8"
backgroundColor="#115675"
textColor="#FFFFFF"
```

## How to run

```
streamlit run app_p2.py
```



## Note:

- Ensure to configure the MySQL database credentials in the `HOSTNAME`, `DATABASE`, `USERNAME`, and `PASSWORD` variables.

