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

PREVIOUSLY ASKED QUESTIONS IN THIS SESSION:
{previous_questions}

CRITICAL RULES FOR QUESTION GENERATION:
1. ABSOLUTELY NO DUPLICATES: Do NOT repeat, rephrase, or ask about the exact same topic as any of the previously asked questions listed above.
2. TOPIC DIVERSITY: Focus on a COMPLETELY NEW technical concept, architectural design pattern, performance concern, database query tuning, security mechanism, or testing strategy relevant to {tech_stack}.
3. DIFFICULTY CALIBRATION: Calibrate question difficulty strictly for a {experience_level} candidate.

You MUST reply ONLY with a raw valid JSON object matching this structure (no markdown fences, no extra text):
{{
  "question_number": {question_number},
  "topic": "<Specific Topic name, e.g. PostgreSQL Indexing & Query Execution Plans>",
  "question_text": "<The actual unique technical interview question>",
  "focus_area": "<What key technical knowledge this question tests>",
  "difficulty": "<Easy | Medium | Hard>"
}}
"""

FALLBACK_TOPICS = [
    {
        "topic": "Core Fundamentals & Modular Design",
        "question_text": "In {tech_stack}, how do you design components for high cohesion and low coupling? Can you walk through a concrete production architecture example?",
        "focus_area": "Clean Architecture & Design Patterns"
    },
    {
        "topic": "Database Optimization & Performance",
        "question_text": "When building backend services with {tech_stack}, how do you identify slow database queries and optimize execution performance?",
        "focus_area": "Database Optimization & SQL Tuning"
    },
    {
        "topic": "Security & Authentication Management",
        "question_text": "How do you secure REST APIs built in {tech_stack} against common vulnerabilities like SQL injection, XSS, and unauthorized token tampering?",
        "focus_area": "API Security & Authorization"
    },
    {
        "topic": "Concurrency, State & Multithreading",
        "question_text": "How do you handle thread safety, race conditions, or asynchronous task execution in {tech_stack} under high concurrent traffic?",
        "focus_area": "Multithreading & Concurrency"
    },
    {
        "topic": "System Resilience & Fault Tolerance",
        "question_text": "What logging, exception handling, and circuit breaker patterns do you implement in {tech_stack} to ensure system reliability during upstream failures?",
        "focus_area": "Resilience & Reliability Engineering"
    },
    {
        "topic": "Caching & Memory Management",
        "question_text": "What caching patterns and memory allocation strategies do you use in {tech_stack} to minimize latency and database load?",
        "focus_area": "Memory Management & Caching"
    }
]

def generate_next_question(
    role: str,
    tech_stack: str,
    experience_level: str,
    question_number: int,
    max_questions: int,
    evaluations: List[Dict[str, Any]] = None,
    previous_questions_list: List[str] = None
) -> Dict[str, Any]:
    llm = get_llm(temperature=0.7)
    
    prev_questions = []
    
    # Extract from passed previous questions list
    if previous_questions_list:
        for idx, q_txt in enumerate(previous_questions_list, 1):
            if q_txt:
                prev_questions.append(f"- Question {idx}: {q_txt}")
                
    # Extract from evaluations list
    if evaluations:
        for ev in evaluations:
            q_txt = ev.get("question_text") or (ev.get("question") or {}).get("question_text")
            q_num = ev.get("question_number", len(prev_questions) + 1)
            if q_txt and f"- Question {q_num}: {q_txt}" not in prev_questions:
                prev_questions.append(f"- Question {q_num}: {q_txt}")
    
    prev_q_str = "\n".join(prev_questions) if prev_questions else "None yet (This is Question 1)."
    
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
        content = re.sub(r"^```json\s*", "", content)
        content = re.sub(r"^```\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        
        parsed = json.loads(content)
        parsed["question_number"] = question_number
        return parsed
    except Exception as e:
        # Dynamic topic fallback based on question_number
        topic_idx = (question_number - 1) % len(FALLBACK_TOPICS)
        fallback_item = FALLBACK_TOPICS[topic_idx]
        
        main_tech = tech_stack.split(',')[0].strip()
        
        return {
            "question_number": question_number,
            "topic": fallback_item["topic"].replace("{tech_stack}", main_tech),
            "question_text": fallback_item["question_text"].replace("{tech_stack}", main_tech).replace("{role}", role),
            "focus_area": fallback_item["focus_area"],
            "difficulty": "Medium",
            "fallback": True
        }

BATCH_QUESTION_PROMPT = """You are an expert Senior Technical Interviewer conducting a mock technical interview.
Target Role: {role}
Tech Stack / Topics: {tech_stack}
Experience Level: {experience_level}
Total Questions to Generate: {max_questions}

CRITICAL RULES FOR BATCH QUESTION GENERATION:
1. Generate EXACTLY {max_questions} distinct, highly relevant technical interview questions for {role} focusing on {tech_stack}.
2. ABSOLUTELY NO DUPLICATES: Each question MUST cover a COMPLETELY DIFFERENT topic, architecture pattern, database optimization, concurrency/state model, API security mechanism, or resilience pattern.
3. DIFFICULTY CALIBRATION: Calibrate question difficulty strictly for a {experience_level} candidate.

You MUST reply ONLY with a raw JSON array of objects matching this structure (no markdown fences, no extra text):
[
  {{
    "question_number": 1,
    "topic": "<Specific Topic 1>",
    "question_text": "<Clear technical interview question 1>",
    "focus_area": "<Focus area>",
    "difficulty": "<Easy | Medium | Hard>"
  }},
  ...
]
"""

def generate_batch_questions(
    role: str,
    tech_stack: str,
    experience_level: str,
    max_questions: int = 5
) -> List[Dict[str, Any]]:
    llm = get_llm(temperature=0.7)
    
    prompt = BATCH_QUESTION_PROMPT.format(
        role=role,
        tech_stack=tech_stack,
        experience_level=experience_level,
        max_questions=max_questions
    )
    
    try:
        response = llm.invoke([
            SystemMessage(content="You are an expert technical interviewer system that outputs raw JSON array only."),
            HumanMessage(content=prompt)
        ])
        
        content = response.content.strip()
        content = re.sub(r"^```json\s*", "", content)
        content = re.sub(r"^```\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        
        parsed = json.loads(content)
        if isinstance(parsed, list) and len(parsed) > 0:
            for idx, q in enumerate(parsed, 1):
                q["question_number"] = idx
            return parsed
    except Exception as e:
        print(f"Error generating batch questions: {e}")
        
    questions = []
    main_tech = tech_stack.split(',')[0].strip()
    pool = list(FALLBACK_TOPICS)
    import random
    random.shuffle(pool)
    
    for i in range(1, max_questions + 1):
        fallback_item = pool[(i - 1) % len(pool)]
        questions.append({
            "question_number": i,
            "topic": fallback_item["topic"].replace("{tech_stack}", main_tech),
            "question_text": fallback_item["question_text"].replace("{tech_stack}", main_tech).replace("{role}", role),
            "focus_area": fallback_item["focus_area"],
            "difficulty": "Medium",
            "fallback": True
        })
    return questions


