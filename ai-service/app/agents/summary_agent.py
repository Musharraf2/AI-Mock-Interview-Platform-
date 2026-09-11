import json
import re
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import get_llm

SUMMARY_PROMPT = """You are a Hiring Committee Lead producing a final technical interview report.

Candidate Role: {role}
Tech Stack: {tech_stack}
Experience Level: {experience_level}

Question & Evaluation History:
{evaluations_summary}

CRITICAL ACCURACY INSTRUCTIONS:
1. Base the overall score STRICTLY on the actual mathematical scores from the Question & Evaluation History above.
2. IF THE CANDIDATE SCORED 0 (e.g., pasted questions back, wrote invalid/empty answers):
   - overall_score MUST BE 0-10 (out of 100).
   - technical_score, communication_score, problem_solving_score MUST BE 0-10.
   - hiring_recommendation MUST BE "No Hire / Reject".
   - summary_verdict MUST state clearly: "Candidate did not provide valid technical answers to the interview questions."
   - top_strengths SHOULD BE [] or ["Attempted interview session"].
3. IF THE CANDIDATE SCORED WELL:
   - Provide accurate breakdown (0-100), hiring_recommendation ("Strong Hire" | "Hire" | "Weak Hire" | "No Hire / Reject"), and constructive 4-week roadmap.

Reply ONLY with a raw JSON object matching this structure (no markdown fences, no extra text):
{{
  "overall_score": 82,
  "technical_score": 80,
  "communication_score": 85,
  "problem_solving_score": 81,
  "hiring_recommendation": "Hire",
  "summary_verdict": "Candidate demonstrated practical knowledge of Spring Boot REST APIs and relational concepts.",
  "top_strengths": [
    "Solid understanding of Spring Security & JWT flow",
    "Clear communication style"
  ],
  "areas_to_improve": [
    "Deep dive into Spring Bean lifecycles",
    "Concurrency & Multithreading primitives"
  ],
  "actionable_roadmap": [
    {{"week": 1, "topic": "Advanced Core Fundamentals", "task": "Study core architecture and component design"}},
    {{"week": 2, "topic": "Concurrency & JVM", "task": "Build thread-safe components"}},
    {{"week": 3, "topic": "Database Indexing", "task": "Analyze SQL query execution plans"}},
    {{"week": 4, "topic": "System Design Practice", "task": "Mock design distributed services"}}
  ]
}}
"""

def generate_final_report(
    role: str,
    tech_stack: str,
    experience_level: str,
    evaluations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    llm = get_llm(temperature=0.3)
    
    summary_lines = []
    total_tech = 0
    total_comm = 0
    total_prob = 0
    count = len(evaluations) if evaluations else 0
    
    for ev in evaluations:
        q_num = ev.get("question_number", 1)
        q_text = ev.get("question_text", "N/A")
        tech_s = ev.get("technical_score", 0)
        comm_s = ev.get("communication_score", 0)
        prob_s = ev.get("problem_solving_score", 0)
        fb = ev.get("feedback_summary", "")
        
        total_tech += tech_s
        total_comm += comm_s
        total_prob += prob_s
        
        summary_lines.append(f"Q{q_num}: {q_text} | Scores: Tech={tech_s}/10, Comm={comm_s}/10, Prob={prob_s}/10 | Feedback: {fb}")
    
    avg_tech_100 = int((total_tech / count) * 10) if count > 0 else 0
    avg_comm_100 = int((total_comm / count) * 10) if count > 0 else 0
    avg_prob_100 = int((total_prob / count) * 10) if count > 0 else 0
    avg_overall = int((avg_tech_100 + avg_comm_100 + avg_prob_100) / 3) if count > 0 else 0
    
    evals_str = "\n".join(summary_lines) if summary_lines else "No questions evaluated."
    
    prompt = SUMMARY_PROMPT.format(
        role=role,
        tech_stack=tech_stack,
        experience_level=experience_level,
        evaluations_summary=evals_str
    )
    
    try:
        response = llm.invoke([
            SystemMessage(content="You are a Hiring Committee Lead. Output raw JSON only."),
            HumanMessage(content=prompt)
        ])
        
        content = response.content.strip()
        content = re.sub(r"^```json\s*", "", content)
        content = re.sub(r"^```\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        
        parsed = json.loads(content)
        
        # Enforce mathematical bounds on score
        if avg_overall == 0:
            parsed["overall_score"] = 0
            parsed["technical_score"] = 0
            parsed["communication_score"] = 0
            parsed["problem_solving_score"] = 0
            parsed["hiring_recommendation"] = "No Hire / Reject"
            parsed["summary_verdict"] = "Candidate did not provide valid technical answers to the interview questions."
            parsed["top_strengths"] = ["Session attempted"]
            
        return parsed
    except Exception as e:
        rec = "No Hire / Reject" if avg_overall < 40 else ("Weak Hire" if avg_overall < 70 else "Hire")
        verdict = "Candidate did not provide valid technical answers to the interview questions." if avg_overall == 0 else f"Candidate demonstrated foundational knowledge for {role}."
        
        return {
            "overall_score": avg_overall,
            "technical_score": avg_tech_100,
            "communication_score": avg_comm_100,
            "problem_solving_score": avg_prob_100,
            "hiring_recommendation": rec,
            "summary_verdict": verdict,
            "top_strengths": ["Attempted mock interview session"] if avg_overall == 0 else ["Good communication", "Understands core concepts"],
            "areas_to_improve": [
                "Provide actual technical explanations instead of repeating question text",
                "Review core framework architecture and design patterns"
            ],
            "actionable_roadmap": [
                {"week": 1, "topic": f"{tech_stack.split(',')[0]} Fundamentals", "task": "Study core language fundamentals & syntax"},
                {"week": 2, "topic": "Component Architecture", "task": "Build basic CRUD applications"},
                {"week": 3, "topic": "Database Basics", "task": "Learn relational database query writing"},
                {"week": 4, "topic": "Mock Interview Practice", "task": "Re-take technical interview drills"}
            ],
            "fallback": True,
            "error": str(e)
        }

