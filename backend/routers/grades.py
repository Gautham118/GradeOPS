from fastapi import APIRouter, Depends
from core.deps import require_role

router = APIRouter(prefix="/grades", tags=["grades"])

@router.get("/")
async def get_grades():
    # To be implemented: GET /grades
    pass

@router.patch("/{grade_id}")
async def update_grade(grade_id: str, user: dict = Depends(require_role("ta"))):
    # To be implemented: PATCH /grades/:id (TA only for PATCH)
    pass
