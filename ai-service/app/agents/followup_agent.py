import json
import re
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import get_llm

FOLLOWUP_PROMPT = """You are a Senior Technical Interviewer conducting an adaptive follow-up question.

Target Role: {role}
Original Question: "{question_text}"
Candidate's Answer: "{candidate_response}"
Evaluator Feedback / Missing Info: "{improvements}"

Your task:
Formulate a concise, focused follow-up question probing the candidate deeper on the missing details or edge cases they didn't cover.

Reply ONLY with a raw JSON object matching this structure (no markdown fences, no extra text):
{{
  "is_followup": true,
  "original_question_text": "{question_text}",
  "followup_question_text": "<Your concise, probing follow-up question>",
  "focus": "<Specific concept being probed>",
  "hint": "<Optional helpful tip if candidate struggles>"
}}
"""

def generate_followup(
    role: str,
    question_text: str,
    candidate_response: str,
    improvements: str
) -> Dict[str, Any]:
    llm = get_llm(temperature=0.5)
    
    prompt = FOLLOWUP_PROMPT.format(
        role=role,
        question_text=question_text,
        candidate_response=candidate_response,
        improvements=improvements
    )
    
    try:
        response = llm.invoke([
            SystemMessage(content="You are an expert technical interviewer probing candidate depth. Output raw JSON only."),
            HumanMessage(content=prompt)
        ])
        
        content = response.content.strip()
        content = re.sub(r"^```json\s*", "", content)
        content = re.sub(r"^```\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        
        return json.loads(content)
    except Exception as e:
        return {
            "is_followup": True,
            "original_question_text": question_text,
            "followup_question_text": f"That makes sense. Can you elaborate further on how you would test or optimize this under heavy load?",
            "focus": "Performance & Scalability",
            "hint": "Think about caching, database indices, or async processing.",
            "fallback": True,
            "error": str(e)
        }
