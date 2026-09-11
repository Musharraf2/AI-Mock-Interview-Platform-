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

Synthesize a comprehensive final performance report for this candidate.
Produce:
1. Overall Weighted Score (0 to 100)
2. Breakdown: Technical Competency (0-100), Communication Clarity (0-100), System Architecture & Problem Solving (0-100)
3. Top 3 Technical Strengths
4. Key Areas Needing Improvement
5. Hiring Recommendation (Strong Hire / Hire / Weak Hire / Re-interview)
6. Actionable 4-Week Learning Roadmap to master missing skills.

Reply ONLY with a raw JSON object matching this structure (no markdown fences, no extra text):
{{
  "overall_score": 82,
  "technical_score": 80,
  "communication_score": 85,
  "problem_solving_score": 81,
  "hiring_recommendation": "Hire",
  "summary_verdict": "Candidate demonstrated strong practical knowledge of Spring Boot REST APIs and relational concepts. Needs deeper mastery of async event handling.",
  "top_strengths": [
    "Solid understanding of Spring Security & JWT flow",
    "Clear communication style with structured answers",
    "Good database query optimization intuition"
  ],
  "areas_to_improve": [
    "Deep dive into Spring Bean lifecycles and circular dependency resolutions",
    "Concurrency & Multithreading primitives in Java 17+"
  ],
  "actionable_roadmap": [
    {{"week": 1, "topic": "Advanced Spring Core", "task": "Study custom bean post-processors and conditional bean creation"}},
    {{"week": 2, "topic": "Concurrency & JVM", "task": "Build thread-safe queue implementation using ReentrantLocks"}},
    {{"week": 3, "topic": "Database Indexing & Locks", "task": "Analyze PostgreSQL query execution plans using EXPLAIN ANALYZE"}},
    {{"week": 4, "topic": "System Design Practice", "task": "Mock design a distributed rate limiter with Redis and Spring Boot"}}
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
    for ev in evaluations:
        q_num = ev.get("question_number", 1)
        q_text = ev.get("question_text", "N/A")
        tech_s = ev.get("technical_score", 7)
        comm_s = ev.get("communication_score", 7)
        fb = ev.get("feedback_summary", "")
        summary_lines.append(f"Q{q_num}: {q_text} | Scores: Tech={tech_s}/10, Comm={comm_s}/10 | Feedback: {fb}")
    
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
        
        return json.loads(content)
    except Exception as e:
        # Fallback structured report
        return {
            "overall_score": 78,
            "technical_score": 76,
            "communication_score": 80,
            "problem_solving_score": 78,
            "hiring_recommendation": "Hire",
            "summary_verdict": f"The candidate demonstrated foundational knowledge for a {role} role using {tech_stack}.",
            "top_strengths": [
                "Good technical communication",
                "Understand core concepts",
                "Practical orientation"
            ],
            "areas_to_improve": [
                "Practice deeper architectural design trade-offs",
                "Review edge case handling in high-throughput applications"
            ],
            "actionable_roadmap": [
                {"week": 1, "topic": f"{tech_stack.split(',')[0]} Mastery", "task": "Review core documentation and advanced features"},
                {"week": 2, "topic": "System Design Patterns", "task": "Implement caching and connection pooling best practices"},
                {"week": 3, "topic": "Database Performance", "task": "Optimize SQL query execution and indexing strategies"},
                {"week": 4, "topic": "Mock Interview Practice", "task": "Conduct timed technical question drills"}
            ],
            "fallback": True,
            "error": str(e)
        }
