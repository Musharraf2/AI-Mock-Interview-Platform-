from langgraph.graph import StateGraph, END
from app.graph.state import InterviewState
from app.agents.question_agent import generate_next_question
from app.agents.evaluator_agent import evaluate_answer
from app.agents.followup_agent import generate_followup
from app.agents.summary_agent import generate_final_report

def question_node(state: InterviewState) -> InterviewState:
    next_q_num = state["question_count"] + 1
    question_data = generate_next_question(
        role=state["role"],
        tech_stack=state["tech_stack"],
        experience_level=state["experience_level"],
        question_number=next_q_num,
        max_questions=state["max_questions"],
        evaluations=state["evaluations"]
    )
    
    state["current_question"] = question_data
    state["question_count"] = next_q_num
    state["chat_history"].append({
        "role": "interviewer",
        "content": question_data.get("question_text", "")
    })
    return state

def evaluation_node(state: InterviewState) -> InterviewState:
    curr_q = state.get("current_question", {})
    response_text = state.get("current_response", "")
    
    eval_res = evaluate_answer(
        role=state["role"],
        experience_level=state["experience_level"],
        question_number=state["question_count"],
        topic=curr_q.get("topic", "General"),
        question_text=curr_q.get("question_text", ""),
        candidate_response=response_text
    )
    
    state["evaluations"].append(eval_res)
    state["needs_followup"] = eval_res.get("needs_followup", False)
    return state

def followup_node(state: InterviewState) -> InterviewState:
    curr_q = state.get("current_question", {})
    last_eval = state["evaluations"][-1] if state["evaluations"] else {}
    improvements = ", ".join(last_eval.get("improvements", []))
    
    followup_data = generate_followup(
        role=state["role"],
        question_text=curr_q.get("question_text", ""),
        candidate_response=state.get("current_response", ""),
        improvements=improvements
    )
    
    state["followup_count"] += 1
    state["needs_followup"] = False
    state["current_question"] = {
        "question_number": state["question_count"],
        "topic": f"{curr_q.get('topic', 'General')} (Follow-up)",
        "question_text": followup_data.get("followup_question_text", ""),
        "focus_area": followup_data.get("focus", "Deep Dive"),
        "is_followup": True
    }
    state["chat_history"].append({
        "role": "interviewer",
        "content": followup_data.get("followup_question_text", "")
    })
    return state

def report_node(state: InterviewState) -> InterviewState:
    final_rep = generate_final_report(
        role=state["role"],
        tech_stack=state["tech_stack"],
        experience_level=state["experience_level"],
        evaluations=state["evaluations"]
    )
    state["final_report"] = final_rep
    return state

def route_after_evaluation(state: InterviewState) -> str:
    if state.get("needs_followup") and state.get("followup_count", 0) < 2:
        return "followup"
    elif state["question_count"] >= state["max_questions"]:
        return "report"
    else:
        return "question"

def build_interview_graph():
    workflow = StateGraph(InterviewState)
    
    workflow.add_node("question", question_node)
    workflow.add_node("evaluate", evaluation_node)
    workflow.add_node("followup", followup_node)
    workflow.add_node("report", report_node)
    
    workflow.set_entry_point("question")
    
    workflow.add_conditional_edges(
        "evaluate",
        route_after_evaluation,
        {
            "followup": "followup",
            "report": "report",
            "question": "question"
        }
    )
    
    workflow.add_edge("followup", "evaluate")
    workflow.add_edge("report", END)
    
    return workflow.compile()
