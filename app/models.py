from pydantic import BaseModel
from typing import Optional


class DocumentRequest(BaseModel):
    text: str

class AnswerRequest(BaseModel):
    answer: str
    session_id: Optional[str] = None    

class GenerateRequest(BaseModel):
    session_id: str

class ScoreRequest(BaseModel):
    session_id: str