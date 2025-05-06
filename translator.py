# 📁 translator.py

from langchain_openai import ChatOpenAI  # Import the OpenAI LLM wrapper from LangChain

# Function to translate a given text to the specified target language
def translate_summary(text, target_language, api_key):
    # Initialize the OpenAI language model
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",       # Use GPT-3.5-turbo model
        openai_api_key=api_key,     # Pass the API key for authentication
        temperature=0               # Set temperature to 0 for deterministic output
    )

    # Create the translation prompt
    prompt = f"Translate the following text to {target_language}:\n\n{text}"

    # Invoke the model with the prompt and return the translated content
    return llm.invoke(prompt).content
