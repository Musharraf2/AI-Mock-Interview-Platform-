import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-1.5-flash")


def get_llm(temperature: float = 0.7, model_name: str = None):
    """
    Initializes and returns a Google Gemini LLM instance.
    Configures automatic fallback from primary model (e.g. Gemini 2.5 Flash)
    to a secondary model (e.g. Gemini 1.5 Flash) in case of rate limits or transient errors,
    without executing any redundant network pings during initialization.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip() or GEMINI_API_KEY
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured. Please set GEMINI_API_KEY in your environment or .env file."
        )

    primary_model = model_name or DEFAULT_MODEL

    primary_llm = ChatGoogleGenerativeAI(
        model=primary_model,
        google_api_key=api_key,
        temperature=temperature,
    )

    # Attach fallback model if different from primary
    if FALLBACK_MODEL and FALLBACK_MODEL != primary_model:
        fallback_llm = ChatGoogleGenerativeAI(
            model=FALLBACK_MODEL,
            google_api_key=api_key,
            temperature=temperature,
        )
        return primary_llm.with_fallbacks([fallback_llm])

    return primary_llm
