from fastapi import APIRouter, Depends, HTTPException
from schemas.exam import ExamCreate, ExamOut
from core.auth import get_current_user
from core.deps import require_role
from core.config import supabase_admin

router = APIRouter()


@router.post("/", response_model=ExamOut)
def create_exam(
    payload: ExamCreate,
    user: dict = Depends(require_role("instructor"))
):
    result = supabase_admin.table("exams").insert({
        "title": payload.title,
        "subject": payload.subject,
        "rubric_json": payload.rubric_json.model_dump(),
        "created_by": user["sub"]
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create exam")
    return result.data[0]


@router.get("/", response_model=list[ExamOut])
def list_exams(user: dict = Depends(get_current_user)):
    result = supabase_admin.table("exams").select("*").execute()
    return result.data


@router.get("/{exam_id}", response_model=ExamOut)
def get_exam(
    exam_id: str,
    user: dict = Depends(get_current_user)
):
    result = supabase_admin.table("exams")\
        .select("*")\
        .eq("id", exam_id)\
        .single()\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Exam not found")
    return result.data