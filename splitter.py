# splitter.py

from langchain_text_splitters import RecursiveCharacterTextSplitter  # Import the text splitter from LangChain

# Function to split long text into manageable chunks
def split_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,        # Maximum number of characters per chunk
        chunk_overlap=100      # Number of overlapping characters between chunks for context preservation
    )
    return splitter.split_text(text)  # Return the list of text chunks
