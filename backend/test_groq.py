
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

# Initialize LangChain ChatGroq
llm = ChatGroq(
    temperature=0,
    model_name="openai/gpt-oss-20b",
    max_tokens=100
)

print("Testing LangChain ChatGroq connection...")

try:
    # Simple invoke (non-streaming)
    response = llm.invoke("Hello, say 'LangChain Test Successful' if you can read this.")
    
    print("Response from LangChain:")
    print(response.content)

except Exception as e:
    print("An error occurred:")
    print(e)
