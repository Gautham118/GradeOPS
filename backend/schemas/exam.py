from pydantic import BaseModel
from typing import Any
import uuid

class RubricCondition(BaseModel):
    description: str
    marks: int

class RubricQuestion(BaseModel):
    id: str
    text: str
    max_marks: int
    conditions: list[RubricCondition]

class RubricJSON(BaseModel):
    questions: list[RubricQuestion]

class ExamCreate(BaseModel):
    title: str
    subject: str | None = None
    rubric_json: RubricJSON

class ExamOut(BaseModel):
    id: uuid.UUID
    title: str
    subject: str | None
    rubric_json: Any
    created_by: uuid.UUID

    class Config:
        from_attributes = True