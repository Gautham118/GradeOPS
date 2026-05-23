from fastapi import APIRouter, Depends, HTTPException
from schemas.grade import GradeOut, TAOverride
from core.auth import get_current_user
from core.deps import require_role
from core.config import supabase_admin
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=list[GradeOut])
def get_grades(
    exam_id: str,
    status: str = "pending_review",
    user: dict = Depends(get_current_user)
):
    result = supabase_admin.table("grades")\
        .select("*")\
        .eq("exam_id", exam_id)\
        .eq("status", status)\
        .order("created_at")\
        .execute()
    return result.data


@router.get("/{grade_id}", response_model=GradeOut)
def get_grade(
    grade_id: str,
    user: dict = Depends(get_current_user)
):
    result = supabase_admin.table("grades")\
        .select("*")\
        .eq("id", grade_id)\
        .single()\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Grade not found")
    return result.data


@router.patch("/{grade_id}", response_model=GradeOut)
def ta_action(
    grade_id: str,
    payload: TAOverride,
    user: dict = Depends(require_role("ta", "instructor"))
):
    allowed_statuses = {"approved", "overridden", "flagged"}
    if payload.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"status must be one of {allowed_statuses}"
        )

    if payload.status == "overridden" and payload.ta_score is None:
        raise HTTPException(
            status_code=400,
            detail="ta_score is required when status is 'overridden'"
        )

    update_data = {
        "status": payload.status,
        "reviewed_by": user["sub"],
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
    }
    if payload.ta_score is not None:
        update_data["ta_score"] = payload.ta_score
    if payload.ta_note:
        update_data["ta_note"] = payload.ta_note

    result = supabase_admin.table("grades")\
        .update(update_data)\
        .eq("id", grade_id)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Grade not found")
    return result.data[0]