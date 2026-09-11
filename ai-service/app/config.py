import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def get_llm(temperature: float = 0.7, model_name: str = "gemini-2.5-flash") -> ChatGoogleGenerativeAI:
    """Initialize and return a Gemini Chat model instance."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_gemini_api_key_here":
        # Fallback to standard environment key if present
        api_key = os.environ.get("GOOGLE_API_KEY", "")
    
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key if api_key else None,
        temperature=temperature,
        convert_system_message_to_human=True
    )
