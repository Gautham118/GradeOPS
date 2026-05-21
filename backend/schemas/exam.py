from pydantic import BaseModel
from typing import List, Dict, Any

class ExamCreate(BaseModel):
    title: str
    subject: str
    rubric_json: Dict[str, Any]

class ExamOut(BaseModel):
    id: str
    title: str
    created_at: str
    # ...
