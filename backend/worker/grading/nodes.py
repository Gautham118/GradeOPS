import json
from core.config import settings, supabase_admin
from .prompts import GRADING_SYSTEM_PROMPT

def parse_rubric(state):
    grade = supabase_admin.table("grades").select("*, submissions(exam_id)").eq("id", state["grade_id"]).single().execute().data
    exam = supabase_admin.table("exams").select("rubric_json").eq("id", grade["submissions"]["exam_id"]).single().execute().data
    rubric_questions = exam["rubric_json"]["questions"]
    rubric = next(q for q in rubric_questions if q["id"] == grade["question_id"])
    return {**state, "transcription": grade["transcription"], "rubric": rubric, "max_marks": rubric["max_marks"]}

def evaluate_partial_credit(state):
    from groq import Groq
    client = Groq(api_key=settings.GROQ_API_KEY)
    
    user_prompt = f"""
STUDENT ANSWER:
{state['transcription']}

RUBRIC:
Question: {state['rubric']['text']}
Max marks: {state['rubric']['max_marks']}
Conditions:
{json.dumps(state['rubric']['conditions'], indent=2)}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": GRADING_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=800,
        temperature=0.1
    )
    result = json.loads(response.choices[0].message.content)
    return {**state, "ai_score": result["awarded_marks"], "breakdown": result["breakdown"], "justification": result["justification"]}

def check_plagiarism(state):
    from .embedder import embed_text, find_similar
    embedding = embed_text(state["transcription"])
    similar = find_similar(embedding, state["grade_id"], threshold=0.92)
    return {**state, "plagiarism_flag": len(similar) > 0, "similar_answers": similar}

def write_result(state):
    supabase_admin.table("grades").update({
        "ai_score": state["ai_score"],
        "max_marks": state["max_marks"],
        "breakdown": state["breakdown"],
        "justification": state["justification"],
        "plagiarism_flag": state["plagiarism_flag"],
        "ai_model_used": "llama-3.3-70b-versatile",
        "status": "pending_review",
    }).eq("id", state["grade_id"]).execute()
    return state
