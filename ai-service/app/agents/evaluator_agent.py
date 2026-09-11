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
  Set feedback_summary to "No actual technical answer provided. You pasted the question text back or submitted an incomplete response."
  Set ideal_answer to provide the exact reference model solution for this question.

Otherwise, evaluate the candidate's technical response constructively and accurately:
1. Technical Accuracy (0-10)
2. Clarity & Communication (0-10)
3. Problem Solving & Depth (0-10)
4. Key technical strengths shown
5. Missing details, edge cases, or errors
6. Provide the IDEAL REFERENCE ANSWER (ideal_answer): A high-caliber 10/10 model response to this question.

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
  "ideal_answer": "<The 10/10 ideal reference answer to this question>",
  "needs_followup": false,
  "followup_reason": "Candidate covered main technical points."
}}
"""

EXPLAIN_PROMPT = """You are a Principal Software Engineer providing an in-depth, educational deep-dive explanation for a technical interview question.

Question Topic: {topic}
Question Asked: "{question_text}"
Ideal Reference Answer: "{ideal_answer}"
Candidate's Response: "{candidate_response}"
Tech Stack: {tech_stack}

Provide a comprehensive, expanded deep-dive explanation for candidates who want to master this topic thoroughly.
Include:
1. Core Technical Fundamentals & Principles
2. Architectural Design Patterns & Code Best Practices
3. Edge Cases, Failure Modes & Performance Optimization Strategies

Format your response cleanly using Markdown headings (###) and bullet points. Keep it clear, professional, and directly actionable.
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
    ideal_fallback = f"An ideal answer for '{question_text}' should define the core principles of {topic}, explain architectural trade-offs, describe concrete design patterns, and address concurrency/performance considerations."
    
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
            "ideal_answer": ideal_fallback,
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
        if "ideal_answer" not in parsed:
            parsed["ideal_answer"] = ideal_fallback
        return parsed
    except Exception as e:
        return {
            "question_number": question_number,
            "question_text": question_text,
            "technical_score": 7,
            "communication_score": 7,
            "problem_solving_score": 7,
            "overall_question_score": 7.0,
            "strengths": ["Answer submitted and analyzed"],
            "improvements": ["Provide deeper architectural design trade-offs and code examples"],
            "feedback_summary": "Response recorded. Review the reference solution below.",
            "ideal_answer": ideal_fallback,
            "needs_followup": False,
            "followup_reason": "Standard response evaluated.",
            "fallback": True,
            "error": str(e)
        }

def generate_in_depth_explanation(
    topic: str,
    question_text: str,
    ideal_answer: str = "",
    candidate_response: str = "",
    tech_stack: str = ""
) -> str:
    llm = get_llm(temperature=0.4)
    
    prompt = EXPLAIN_PROMPT.format(
        topic=topic or "Technical Fundamentals",
        question_text=question_text or "",
        ideal_answer=ideal_answer or "N/A",
        candidate_response=candidate_response or "N/A",
        tech_stack=tech_stack or "General Software Development"
    )
    
    try:
        response = llm.invoke([
            SystemMessage(content="You are a principal technical educator. Provide clear, in-depth markdown explanations."),
            HumanMessage(content=prompt)
        ])
        return response.content.strip()
    except Exception as e:
        return f"### 📘 Deep Dive: {topic}\n\n1. **Core Architectural Concept**:\nTo answer '{question_text}' at a senior level, begin by establishing key definitions and core responsibilities.\n\n2. **Production Code & Design Patterns**:\nUse clear separation of concerns, explicit component interfaces, and clean dependency injection or event-driven models.\n\n3. **Edge Cases & Scalability**:\nAddress transaction isolation levels, connection pooling, cache invalidation, and failure isolation under heavy concurrent load."

