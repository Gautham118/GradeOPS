from pydantic import BaseModel
from typing import Any
import uuid

class GradeOut(BaseModel):
    id: uuid.UUID
    submission_id: uuid.UUID
    exam_id: uuid.UUID
    question_id: str
    transcription: str | None
    crop_url: str | None
    ai_score: int | None
    max_marks: int | None
    breakdown: Any
    justification: str | None
    status: str
    plagiarism_flag: bool
    ta_score: int | None
    ta_note: str | None

    class Config:
        from_attributes = True

class TAOverride(BaseModel):
    status: str          # "approved" | "overridden" | "flagged"
    ta_score: int | None = None
    ta_note: str | None = None