import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from core.config import supabase_admin, settings
from worker.grading.prompts import GRADING_SYSTEM_PROMPT
from worker.grading.embedder import embed_and_store, check_plagiarism

llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0
)


def parse_rubric(state: dict) -> dict:
    """Node 1: Load grade record + rubric from DB."""
    grade_id = state["grade_id"]

    grade = supabase_admin.table("grades")\
        .select("*, submissions(exam_id), exams(rubric_json)")\
        .eq("id", grade_id)\
        .single()\
        .execute().data

    # Find this question's rubric
    rubric_json = grade["exams"]["rubric_json"]
    question_rubric = next(
        (q for q in rubric_json["questions"] if q["id"] == grade["question_id"]),
        None
    )

    return {
        **state,
        "transcription": grade["transcription"] or "",
        "question_rubric": question_rubric,
        "max_marks": question_rubric["max_marks"] if question_rubric else 10,
    }


def evaluate_partial_credit(state: dict) -> dict:
    """Node 2: Call LLM to evaluate answer against rubric conditions."""
    transcription = state["transcription"]
    question_rubric = state["question_rubric"]

    if not transcription or transcription.strip() == "":
        return {
            **state,
            "ai_score": 0,
            "breakdown": [],
            "justification": "No answer provided."
        }

    prompt = f"""Question: {question_rubric['text']}

Student's Answer:
{transcription}

Rubric Conditions:
{json.dumps(question_rubric['conditions'], indent=2)}

Max marks: {question_rubric['max_marks']}"""

    response = llm.invoke([
        SystemMessage(content=GRADING_SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ])

    # Parse JSON response
    try:
        raw = response.content.strip()
        # Strip markdown code blocks if model adds them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw.strip())
    except json.JSONDecodeError:
        result = {
            "awarded_marks": 0,
            "max_marks": state["max_marks"],
            "breakdown": [],
            "justification": f"JSON parse error. Raw: {response.content[:200]}"
        }

    return {
        **state,
        "ai_score": result.get("awarded_marks", 0),
        "breakdown": result.get("breakdown", []),
        "justification": result.get("justification", "")
    }


def check_plagiarism_node(state: dict) -> dict:
    """Node 3: Embed answer and check for plagiarism."""
    transcription = state["transcription"]
    grade_id = state["grade_id"]
    question_id_val = state.get("question_id", "q1")

    if not transcription or len(transcription.strip()) < 20:
        return {**state, "plagiarism_flag": False}

    embedding = embed_and_store(grade_id, question_id_val, transcription)
    is_flagged = check_plagiarism(grade_id, question_id_val, embedding)

    if is_flagged:
        print(f"[GRADING] ⚠️  Plagiarism flagged for grade {grade_id}")

    return {**state, "plagiarism_flag": is_flagged}


def write_result(state: dict) -> dict:
    """Node 4: Write final grading result to DB."""
    supabase_admin.table("grades").update({
        "ai_score": state["ai_score"],
        "max_marks": state["max_marks"],
        "breakdown": state["breakdown"],
        "justification": state["justification"],
        "plagiarism_flag": state["plagiarism_flag"],
        "ai_model_used": "llama-3.3-70b-versatile",
        "status": "pending_review"
    }).eq("id", state["grade_id"]).execute()

    print(f"[GRADING] Written → grade {state['grade_id']} | score {state['ai_score']}/{state['max_marks']}")
    return state