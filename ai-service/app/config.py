import os
from dotenv import load_dotenv
from langchain_xai import ChatXAI

load_dotenv()

XAI_API_KEY = os.getenv("XAI_API_KEY", "")


def get_llm(temperature: float = 0.7, model_name: str = "grok-beta") -> ChatXAI:
    """Initialize and return a Grok (xAI) Chat model instance."""
    api_key = os.getenv("XAI_API_KEY", "")

    if not api_key:
        raise ValueError("XAI_API_KEY environment variable is missing or empty.")

    return ChatXAI(
        model=model_name,
        xai_api_key=api_key,
        temperature=temperature,
    )