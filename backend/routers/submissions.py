from fastapi import APIRouter, Depends, UploadFile, File
from core.deps import require_role
from typing import List

router = APIRouter(prefix="/submissions", tags=["submissions"])

@router.post("/bulk")
async def bulk_upload_submissions(
    exam_id: str,
    files: List[UploadFile] = File(...),
    user: dict = Depends(require_role("instructor"))
):
    # To be implemented: POST /submissions/bulk (multipart, instructor only)
    pass
