from pydantic.v1 import BaseModel



class DocumentRequest(BaseModel):
    text: str

class AnswerRequest(BaseModel):
    session_id: str
    answer: str    

class GenerateRequest(BaseModel):
    session_id: str

class ScoreRequest(BaseModel):
    session_id: str