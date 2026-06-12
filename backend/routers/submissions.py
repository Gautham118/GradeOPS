from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import Annotated, List
from schemas.submission import SubmissionOut
from core.deps import require_role
from core.config import supabase_admin
import uuid

router = APIRouter()


@router.post("/bulk", response_model=dict)
async def upload_bulk(
    exam_id: Annotated[str, Form()],
    student_names: Annotated[str, Form()],
    files: List[UploadFile] = File(...),          # multiple files — Swagger renders this correctly
    user: dict = Depends(require_role("instructor"))
):
    names = [n.strip() for n in student_names.split(",")]
    # files = [file]                         # wrap in list so rest of code unchanged

    if len(files) != len(names):
        raise HTTPException(
            status_code=400,
            detail=f"Got {len(files)} files but {len(names)} names. Must match."
        )

    # Verify exam exists
    exam = supabase_admin.table("exams")\
        .select("id")\
        .eq("id", exam_id)\
        .single()\
        .execute()
    if not exam.data:
        raise HTTPException(status_code=404, detail="Exam not found")

    created = []
    for file, student_name in zip(files, names):
        # Validate file type
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"{file.filename} is not a PDF")

        pdf_bytes = await file.read()
        pdf_path = f"{exam_id}/{uuid.uuid4()}.pdf"

        # Upload to Supabase Storage
        supabase_admin.storage.from_("exam-pdfs").upload(
            pdf_path,
            pdf_bytes,
            {"content-type": "application/pdf"}
        )

        # Create submission record
        result = supabase_admin.table("submissions").insert({
            "exam_id": exam_id,
            "student_name": student_name,
            "pdf_path": pdf_path,
            "status": "uploaded",
            "uploaded_by": user["sub"]
        }).execute()

        submission = result.data[0]
        created.append(submission)

        # Enqueue OCR task — uncomment after Day 4
        from worker.tasks import run_ocr_task
        run_ocr_task.delay(submission["id"])

    return {
        "message": f"{len(created)} submissions uploaded successfully",
        "submissions": created
    }


@router.get("/", response_model=list[SubmissionOut])
def list_submissions(
    exam_id: str,
    user: dict = Depends(require_role("instructor"))
):
    result = supabase_admin.table("submissions")\
        .select("*")\
        .eq("exam_id", exam_id)\
        .execute()
    return result.data