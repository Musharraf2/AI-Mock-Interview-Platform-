# LangGraph Multi-Agent Architecture & Workflow

This document details the multi-agent design, system prompts, graph state management, and execution lifecycle powering the **AI Mock Interview Platform**.

---

## 🧠 LangGraph State Machine Architecture

LangGraph provides a **stateful directed graph (`StateGraph`)** where each node represents an autonomous AI agent, and edges represent conditional logic or state transitions.

```
+-------------------------------------------------------------------+
|                        InterviewState                             |
|                                                                   |
|  - role: str                                                      |
|  - tech_stack: str                                                |
|  - experience_level: str                                          |
|  - question_count: int                                            |
|  - max_questions: int                                             |
|  - chat_history: List[Dict[str, str]]                             |
|  - current_question: Dict[str, Any]                               |
|  - current_response: str                                          |
|  - evaluations: List[Dict[str, Any]]                              |
|  - needs_followup: bool                                           |
|  - followup_count: int                                            |
|  - final_report: Dict[str, Any]                                   |
+-------------------------------------------------------------------+
                                  |
                                  v
                    +---------------------------+
                    | Question Generator Agent  |
                    +---------------------------+
                                  |
                                  v
                    +---------------------------+
                    |  Answer Evaluator Agent   |
                    +---------------------------+
                                  |
               +------------------+------------------+
               | (needs_followup)                    | (no followup)
               v                                     v
+---------------------------+         +---------------------------+
|  Adaptive Followup Agent  |         | Check max_questions       |
+---------------------------+         +---------------------------+
               |                                 |            |
               v                                 v (yes)      v (no)
    Return to Evaluator              +----------------+   +--------------------+
                                     | Final Summary  |   | Question Generator |
                                     | Agent          |   +--------------------+
                                     +----------------+
```

---

## 🤖 Detailed Agent Breakdown

### 1. Question Generation Agent (`question_agent.py`)
- **Role**: Senior Technical Interviewer.
- **Input Context**: Candidate Role, Tech Stack, Experience Level, Previous Questions asked in current session.
- **Task**: Formulate the next technical question while avoiding duplicate topics and adapting difficulty to candidate experience level.
- **Output Schema (JSON)**:
  ```json
  {
    "question_number": 1,
    "topic": "Spring Boot Dependency Injection",
    "question_text": "Can you explain the difference between @Autowired field injection and constructor injection in Spring Boot?",
    "focus_area": "Clean Architecture & Bean Lifecycle",
    "difficulty": "Medium"
  }
  ```

---

### 2. Answer Evaluation Agent (`evaluator_agent.py`)
- **Role**: Principal Software Engineer.
- **Input Context**: Role, Experience Level, Topic, Question Text, Candidate Answer.
- **Task**: Evaluate response rigorously across Technical Accuracy, Communication Clarity, and System Design Depth. Determine if candidate missed key concepts requiring a follow-up probe.
- **Output Schema (JSON)**:
  ```json
  {
    "question_number": 1,
    "question_text": "...",
    "technical_score": 8,
    "communication_score": 9,
    "problem_solving_score": 7,
    "overall_question_score": 8.0,
    "strengths": ["Clear explanation of dependency injection"],
    "improvements": ["Did not address bean scope lifecycles"],
    "feedback_summary": "Solid answer. Mention bean scopes for bonus depth.",
    "needs_followup": false,
    "followup_reason": "Covered primary technical points."
  }
  ```

---

### 3. Adaptive Follow-up Agent (`followup_agent.py`)
- **Role**: Probing Technical Interviewer.
- **Input Context**: Original Question, Candidate Answer, Evaluator's identified missing key points.
- **Task**: Generate a focused follow-up question probing deeper into missing edge cases or ambiguous statements.
- **Output Schema (JSON)**:
  ```json
  {
    "is_followup": true,
    "original_question_text": "...",
    "followup_question_text": "How would you handle circular dependencies between two constructor-injected Spring components?",
    "focus": "Circular Dependency Resolution",
    "hint": "Think about @Lazy annotation or setter injection fallback."
  }
  ```

---

### 4. Final Summary & Roadmap Agent (`summary_agent.py`)
- **Role**: Hiring Committee Lead.
- **Input Context**: Candidate Role, Tech Stack, Experience Level, Full List of Question Evaluations.
- **Task**: Synthesize overall performance scores, hiring recommendation (`Strong Hire`, `Hire`, `Weak Hire`), top strengths, major weaknesses, and construct an actionable **4-week learning roadmap**.
- **Output Schema (JSON)**:
  ```json
  {
    "overall_score": 82,
    "technical_score": 80,
    "communication_score": 85,
    "problem_solving_score": 81,
    "hiring_recommendation": "Hire",
    "summary_verdict": "Candidate demonstrated strong practical knowledge of Spring Boot REST APIs and relational concepts.",
    "top_strengths": [
      "Solid understanding of Spring Security & JWT flow",
      "Clear communication style"
    ],
    "areas_to_improve": [
      "Deep dive into Spring Bean lifecycles",
      "Concurrency & Multithreading primitives"
    ],
    "actionable_roadmap": [
      {"week": 1, "topic": "Advanced Spring Core", "task": "Study custom bean post-processors"},
      {"week": 2, "topic": "Concurrency in Java", "task": "Build thread-safe queue implementation"},
      {"week": 3, "topic": "Database Indexing", "task": "Analyze PostgreSQL execution plans"},
      {"week": 4, "topic": "System Design Practice", "task": "Mock design a distributed rate limiter"}
    ]
  }
  ```

---

## 🛡️ Resilience & Fallback Design

To guarantee 99.9% availability even if the external LLM provider experiences network latency or rate limits, each agent includes a **safe fallback mechanism**:
- **JSON Markdown Cleaning**: Custom regex (`re.sub`) strips any accidental ```json block wrappers returned by LLMs.
- **Structured Exception Handlers**: If JSON parsing or API calls fail, the agent gracefully returns a structured fallback response so the user's interview flow is never interrupted.
