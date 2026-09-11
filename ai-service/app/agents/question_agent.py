import json
import re
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import get_llm

QUESTION_PROMPT = """You are an expert Senior Technical Interviewer conducting a mock technical interview.
Target Role: {role}
Tech Stack / Skills: {tech_stack}
Experience Level: {experience_level}
Current Question Number: {question_number} of {max_questions}

Previous Questions Asked:
{previous_questions}

Your goal:
Generate the next realistic technical interview question.
- Make it relevant to the candidate's role and tech stack.
- Adapt difficulty according to the experience level ({experience_level}).
- Ensure the question tests problem-solving, architectural awareness, or core technical concepts.

You MUST reply ONLY with a valid JSON object matching this structure (no markdown fences, no extra text):
{{
  "question_number": {question_number},
  "topic": "<Specific Topic, e.g. Spring Boot Dependency Injection, SQL Indexing>",
  "question_text": "<The actual technical interview question>",
  "focus_area": "<What key technical knowledge this question tests>",
  "difficulty": "<Easy | Medium | Hard>"
}}
"""

def generate_next_question(
    role: str,
    tech_stack: str,
    experience_level: str,
    question_number: int,
    max_questions: int,
    evaluations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    llm = get_llm(temperature=0.7)
    
    prev_questions = []
    for ev in evaluations:
        if "question_text" in ev:
            prev_questions.append(f"- Question {ev.get('question_number')}: {ev.get('question_text')}")
    
    prev_q_str = "\n".join(prev_questions) if prev_questions else "None yet."
    
    prompt = QUESTION_PROMPT.format(
        role=role,
        tech_stack=tech_stack,
        experience_level=experience_level,
        question_number=question_number,
        max_questions=max_questions,
        previous_questions=prev_q_str
    )
    
    try:
        response = llm.invoke([
            SystemMessage(content="You are an expert technical interviewer system that outputs raw JSON only."),
            HumanMessage(content=prompt)
        ])
        
        content = response.content.strip()
        # Clean JSON markdown blocks if present
        content = re.sub(r"^```json\s*", "", content)
        content = re.sub(r"^```\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        
        parsed = json.loads(content)
        return parsed
    except Exception as e:
        # Fallback question structure if LLM key is missing or formatting fails
        return {
            "question_number": question_number,
            "topic": f"{tech_stack.split(',')[0]} Fundamentals",
            "question_text": f"Can you explain the core architectural principles of {tech_stack.split(',')[0]} and how you handle state management or scalability for a {role} role?",
            "focus_area": "Core Concepts & Architecture",
            "difficulty": "Medium",
            "fallback": True,
            "error": str(e)
        }
