import os
import requests
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

XAI_API_KEY = os.getenv("XAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

class GrokDirectChat(BaseChatModel):
    xai_api_key: str
    model_name: str = "grok-beta"
    temperature: float = 0.7

    @property
    def _llm_type(self) -> str:
        return "xai-grok"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        payload_messages = []
        for m in messages:
            if isinstance(m, SystemMessage):
                payload_messages.append({"role": "system", "content": m.content})
            elif isinstance(m, HumanMessage):
                payload_messages.append({"role": "user", "content": m.content})
            elif isinstance(m, AIMessage):
                payload_messages.append({"role": "assistant", "content": m.content})
            else:
                payload_messages.append({"role": "user", "content": str(m.content)})

        headers = {
            "Authorization": f"Bearer {self.xai_api_key}",
            "Content-Type": "application/json"
        }
        body = {
            "model": self.model_name,
            "messages": payload_messages,
            "temperature": self.temperature
        }

        resp = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=body, timeout=30)
        
        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            message = AIMessage(content=content)
            generation = ChatGeneration(message=message)
            return ChatResult(generations=[generation])
        else:
            raise Exception(f"xAI API returned HTTP {resp.status_code}: {resp.text}")

def get_llm(temperature: float = 0.7, model_name: str = "grok-beta"):
    """
    Initialize and return LLM.
    Tries Grok xAI API first if key exists. If xAI fails or has 0 credits (HTTP 403),
    falls back seamlessly to Gemini 2.5 Flash API.
    """
    xai_key = os.getenv("XAI_API_KEY", "").strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "AIzaSyA6ybRB_WmkQF8_8cK45DtVefHvMqlBi1U").strip()

    if xai_key:
        try:
            grok = GrokDirectChat(xai_api_key=xai_key, model_name=model_name, temperature=temperature)
            # Test invocation to check if team has credits
            grok.invoke([HumanMessage(content="test")])
            return grok
        except Exception as e:
            print(f"[AI Service Config] xAI Grok API Key check failed ({e}). Switching to Gemini 2.5 Flash API.")

    if gemini_key:
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=gemini_key,
            temperature=temperature
        )

    raise ValueError("No valid LLM API keys found.")
