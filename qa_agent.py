from langchain.agents import Tool, AgentType, initialize_agent  # Import LangChain agent-related utilities
from langchain.chat_models import ChatOpenAI  # Import the chat model interface
from langsmith import traceable  # Import LangSmith tracking decorator

# Global variable to hold the transcript content
global_transcript = ""

# Function to set the global transcript from outside
def set_transcript(text):
    global global_transcript
    global_transcript = text

# Decorated agent builder function that LangSmith will track
@traceable(name="Video Q&A Agent")  # LangSmith will automatically trace this for debugging/analytics
def build_agent(openai_api_key):  # Function takes in OpenAI API key to authenticate the model
    if not global_transcript:
        raise ValueError("❌ No transcript available. Please upload a video and transcribe first.")

    # Internal QA function that searches for the query in the transcript
    def video_qa_tool(query):
        if query.lower() not in global_transcript.lower():
            return "The question is outside the scope of the video."
        return f"{global_transcript}\n\nAnswer to your question: {query}"

    # Define the tool that the agent can use
    tools = [
        Tool(
            name="VideoQA",
            func=video_qa_tool,
            description="Answers questions strictly from the video transcript."
        )
    ]

    # Initialize the language model
    llm = ChatOpenAI(
        model="gpt-4",
        openai_api_key=openai_api_key,  # Use provided OpenAI key
        temperature=0  # Make output deterministic
    )

    # Create the agent using LangChain with the defined tool and model
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False
    )
    return agent  # Return the constructed agent
