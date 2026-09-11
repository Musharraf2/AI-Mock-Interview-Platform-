from typing import TypedDict, List, Dict, Any, Optional

class InterviewState(TypedDict):
    role: str
    tech_stack: str
    experience_level: str
    question_count: int
    max_questions: int
    chat_history: List[Dict[str, str]]
    current_question: Optional[Dict[str, Any]]
    current_response: Optional[str]
    evaluations: List[Dict[str, Any]]
    needs_followup: bool
    followup_count: int
    final_report: Optional[Dict[str, Any]]
