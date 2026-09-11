import json
import re
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import get_llm

EVALUATION_PROMPT = """You are a Principal Software Engineer evaluating a candidate's answer during a mock technical interview.

Candidate Target Role: {role}
Experience Level: {experience_level}
Question Topic: {topic}
Question Asked: "{question_text}"

Candidate's Answer:
"{candidate_response}"

Evaluate the candidate's response rigorously but constructively.
Check for:
1. Technical Accuracy (1-10)
2. Clarity & Communication (1-10)
3. Problem Solving & Depth (1-10)
4. Key strengths shown in the response
5. Missing details, edge cases, or errors in the response
6. Decision: Does this answer need a probe/follow-up question because the candidate missed crucial details or made an ambiguous statement? (True/False)

Reply ONLY with a raw JSON object matching this structure (no markdown fences, no extra text):
{{
  "question_number": {question_number},
  "question_text": "{question_text}",
  "technical_score": 8,
  "communication_score": 9,
  "problem_solving_score": 7,
  "overall_question_score": 8.0,
  "strengths": ["Clear explanation of dependency injection", "Mentioned interface-based decoupling"],
  "improvements": ["Did not address bean scope lifecycles (Singleton vs Prototype)"],
  "feedback_summary": "Solid foundation demonstrated. To improve, mention bean lifecycles and thread safety.",
  "needs_followup": false,
  "followup_reason": "Candidate covered main aspects well."
}}
"""

def evaluate_answer(
    role: str,
    experience_level: str,
    question_number: int,
    topic: str,
    question_text: str,
    candidate_response: str
) -> Dict[str, Any]:
    llm = get_llm(temperature=0.3)
    
    prompt = EVALUATION_PROMPT.format(
        role=role,
        experience_level=experience_level,
        topic=topic,
        question_text=question_text,
        question_number=question_number,
        candidate_response=candidate_response
    )
    
    try:
        response = llm.invoke([
            SystemMessage(content="You are a principal technical interviewer evaluating answers. Output raw JSON only."),
            HumanMessage(content=prompt)
        ])
        
        content = response.content.strip()
        content = re.sub(r"^```json\s*", "", content)
        content = re.sub(r"^```\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        
        parsed = json.loads(content)
        return parsed
    except Exception as e:
        return {
            "question_number": question_number,
            "question_text": question_text,
            "technical_score": 7,
            "communication_score": 7,
            "problem_solving_score": 7,
            "overall_question_score": 7.0,
            "strengths": ["Response received and processed"],
            "improvements": ["Provide more concrete production examples"],
            "feedback_summary": "Good response. Be sure to elaborate on edge cases and performance considerations.",
            "needs_followup": False,
            "followup_reason": "Standard answer evaluated.",
            "fallback": True,
            "error": str(e)
        }
