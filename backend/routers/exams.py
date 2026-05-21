from fastapi import APIRouter, Depends
from core.deps import require_role

router = APIRouter(prefix="/exams", tags=["exams"])

@router.post("/")
async def create_exam(user: dict = Depends(require_role("instructor"))):
    # To be implemented: POST /exams (instructor only)
    pass

@router.get("/")
async def get_exams():
    # To be implemented: GET /exams
    pass
