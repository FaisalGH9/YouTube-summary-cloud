# vector_store.py

from langchain_community.vectorstores import Chroma  # Import Chroma vector store (community version)
from langchain.embeddings import OpenAIEmbeddings    # Import OpenAI embeddings for text representation
from langchain.schema import Document                # Import Document schema for storing text chunks

# Function to store text chunks in a persistent Chroma vector database
def store_chunks_persistent(chunks, openai_api_key):
    # Convert each text chunk into a LangChain Document object
    docs = [Document(page_content=chunk) for chunk in chunks]

    # Initialize Chroma vector store with OpenAI embeddings
    vectordb = Chroma.from_documents(
        docs,
        embedding=OpenAIEmbeddings(openai_api_key=openai_api_key),  # Use OpenAI to embed each chunk
        persist_directory="chroma/"  # Path where the vector database will be saved
    )

    # Save the database to disk
    vectordb.persist()

    # Return a retriever interface for searching similar content later
    return vectordb.as_retriever()
