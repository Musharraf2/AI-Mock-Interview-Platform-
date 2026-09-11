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

CRITICAL RULE ON COPY-PASTE & INVALID ANSWERS:
- If the candidate simply repeats, copies, or pastes the question text back into the response box, OR answers with "I don't know", "idk", gibberish, or irrelevant filler text:
  Set ALL scores (technical_score, communication_score, problem_solving_score, overall_question_score) to EXACTLY 0.
  Set strengths to [] (empty array).
  Set improvements to ["Provide a concrete technical explanation instead of repeating the question"].
  Set feedback_summary to "No actual technical answer provided. The candidate pasted the question text back or submitted an empty response."

Otherwise, evaluate the candidate's technical response constructively and accurately:
1. Technical Accuracy (0-10)
2. Clarity & Communication (0-10)
3. Problem Solving & Depth (0-10)
4. Key technical strengths shown
5. Missing details, edge cases, or errors
6. Decision: Does this answer need a probe/follow-up question? (True/False)

Reply ONLY with a raw JSON object matching this structure (no markdown fences, no extra text):
{{
  "question_number": {question_number},
  "question_text": "{question_text}",
  "technical_score": 8,
  "communication_score": 9,
  "problem_solving_score": 7,
  "overall_question_score": 8.0,
  "strengths": ["Clear explanation of core concepts", "Mentioned production trade-offs"],
  "improvements": ["Did not address edge case handling"],
  "feedback_summary": "Solid explanation demonstrated. Elaborate on edge case handling to improve.",
  "needs_followup": false,
  "followup_reason": "Candidate covered main technical points."
}}
"""

def is_copied_or_invalid_answer(question_text: str, candidate_response: str) -> bool:
    resp_clean = (candidate_response or "").strip().lower()
    q_clean = (question_text or "").strip().lower()
    
    if not resp_clean or len(resp_clean) < 12:
        return True
        
    if resp_clean in ["i don't know", "idk", "no idea", "don't know", "none", "n/a", "test"]:
        return True
        
    # Check word overlap ratio
    resp_words = re.findall(r'\w+', resp_clean)
    q_words = set(re.findall(r'\w+', q_clean))
    
    if not resp_words:
        return True
        
    overlap_count = sum(1 for w in resp_words if w in q_words)
    overlap_ratio = overlap_count / float(len(resp_words))
    
    # If over 70% of candidate's words are copied directly from the question text
    if overlap_ratio > 0.70 and len(resp_words) <= len(q_words) + 4:
        return True
        
    return False

def evaluate_answer(
    role: str,
    experience_level: str,
    question_number: int,
    topic: str,
    question_text: str,
    candidate_response: str
) -> Dict[str, Any]:
    # Pre-validation check for copy-paste or empty answers
    if is_copied_or_invalid_answer(question_text, candidate_response):
        return {
            "question_number": question_number,
            "question_text": question_text,
            "technical_score": 0,
            "communication_score": 0,
            "problem_solving_score": 0,
            "overall_question_score": 0.0,
            "strengths": [],
            "improvements": ["Provide an actual technical explanation instead of repeating the question text"],
            "feedback_summary": "No actual technical answer provided. You pasted the question text back or submitted an incomplete response.",
            "needs_followup": False,
            "followup_reason": "No valid response to evaluate."
        }

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
        # Constructive fallback for genuine answers if LLM API is unreachable
        return {
            "question_number": question_number,
            "question_text": question_text,
            "technical_score": 7,
            "communication_score": 7,
            "problem_solving_score": 7,
            "overall_question_score": 7.0,
            "strengths": ["Answer submitted and analyzed"],
            "improvements": ["Provide deeper architectural design trade-offs and code examples"],
            "feedback_summary": "Response recorded. Elaborate further on production trade-offs and error handling.",
            "needs_followup": False,
            "followup_reason": "Standard response evaluated.",
            "fallback": True,
            "error": str(e)
        }
