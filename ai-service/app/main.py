import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from app.agents.question_agent import generate_next_question
from app.agents.evaluator_agent import evaluate_answer
from app.agents.followup_agent import generate_followup
from app.agents.summary_agent import generate_final_report

app = FastAPI(
    title="AI Mock Interview Platform - LangGraph Microservice",
    description="Multi-Agent AI service powered by LangGraph & Gemini API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Data Schemas ---
class StartSessionRequest(BaseModel):
    role: str = Field(..., example="Java Backend Developer")
    tech_stack: str = Field(..., example="Spring Boot, PostgreSQL, Docker")
    experience_level: str = Field(..., example="Junior")
    max_questions: int = Field(default=5, example=5)
    question_number: int = Field(default=1, example=1)
    previous_questions: List[str] = []
    evaluations: List[Dict[str, Any]] = []

class EvaluateAnswerRequest(BaseModel):
    role: str
    tech_stack: str
    experience_level: str
    question_number: int
    topic: str
    question_text: str
    candidate_response: str
    evaluations_so_far: List[Dict[str, Any]] = []

class FinalReportRequest(BaseModel):
    role: str
    tech_stack: str
    experience_level: str
    evaluations: List[Dict[str, Any]]

# --- API Endpoints ---
@app.get("/health")
def health_check():
    return {
        "status": "UP",
        "service": "AI LangGraph Microservice",
        "llm_provider": "Google Gemini API"
    }

@app.post("/api/ai/generate-question")
def api_generate_question(req: StartSessionRequest):
    """Generates the technical question for a session."""
    try:
        q_data = generate_next_question(
            role=req.role,
            tech_stack=req.tech_stack,
            experience_level=req.experience_level,
            question_number=req.question_number,
            max_questions=req.max_questions,
            evaluations=req.evaluations,
            previous_questions_list=req.previous_questions
        )
        return {"status": "success", "question": q_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/evaluate")
def api_evaluate_answer(req: EvaluateAnswerRequest):
    """Evaluates candidate response and decides if follow-up is needed."""
    try:
        evaluation = evaluate_answer(
            role=req.role,
            experience_level=req.experience_level,
            question_number=req.question_number,
            topic=req.topic,
            question_text=req.question_text,
            candidate_response=req.candidate_response
        )
        
        followup = None
        if evaluation.get("needs_followup"):
            improvements = ", ".join(evaluation.get("improvements", []))
            followup = generate_followup(
                role=req.role,
                question_text=req.question_text,
                candidate_response=req.candidate_response,
                improvements=improvements
            )
            
        return {
            "status": "success",
            "evaluation": evaluation,
            "followup": followup
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/final-report")
def api_generate_final_report(req: FinalReportRequest):
    """Compiles overall candidate report and roadmap."""
    try:
        report = generate_final_report(
            role=req.role,
            tech_stack=req.tech_stack,
            experience_level=req.experience_level,
            evaluations=req.evaluations
        )
        return {"status": "success", "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
