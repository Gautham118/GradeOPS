from pydantic import BaseModel
import uuid

class SubmissionOut(BaseModel):
    id: uuid.UUID
    exam_id: uuid.UUID
    student_name: str
    pdf_path: str
    status: str

    class Config:
        from_attributes = True