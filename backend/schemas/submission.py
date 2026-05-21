from pydantic import BaseModel

class SubmissionOut(BaseModel):
    id: str
    exam_id: str
    status: str
    # ...
