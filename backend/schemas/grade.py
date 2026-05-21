from pydantic import BaseModel
from typing import Optional, Literal

class GradeOut(BaseModel):
    id: str
    submission_id: str
    ai_score: int
    # ...

class TAOverride(BaseModel):
    action: Literal["approve", "override", "flag"]
    ta_score: Optional[int] = None
    ta_note: Optional[str] = None
