import uuid
import app.models
from fastapi import FastAPI
from dotenv import load_dotenv
import os
from app.assessment import assess_document
from pydantic import BaseModel
from app.clarification import generate_question
from app.generation import generate_frd
from app.scoring import score_frd
import uuid



# Temporary in-memory session (simple version)
sessions= {}

load_dotenv()
app = FastAPI(title="AI FRDs Intelligence Engine")

class DocumentRequest(BaseModel):
    text: str

class AnswerRequest(BaseModel):
    session_id: str
    answer: str    

class GenerateRequest(BaseModel):
    session_id: str

class ScoreRequest(BaseModel):
    session_id: str

@app.post("/assess")
def assess(req: DocumentRequest):
    result = assess_document(req.text)
    return result

@app.post("/start_clarification")
def start_clarification(req: DocumentRequest):
    assessment = assess_document(req.text)

    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "context": req.text,
        "missing": assessment.get("missing_sections", []),
        "answers": [],
        "question_count": 0,
        "generated_frd": {},
        "health_score": {}
    }

    question = generate_question(req.text, sessions[session_id]["missing"])

    return {
        "sessioin_id": session_id,
        "question": question

    }



@app.post("/answer")
def answer_question(req: AnswerRequest):
    session = sessions.get(req.session_id)
    if not session:
        return {"error": "Invalid session_id"}
    
    session["answers"].append(req.answer)
    session["question_count"] += 1

    if session["question_count"] >= 5:
        return {"message": "Enough information collected. Ready for FRD generation."}

    combined_context = session["context"] + "\n".join(session["answers"])

    next_question = generate_question(combined_context, session["missing"])

    return {
        "question": next_question
    }

@app.post("/generate")
def generate(req: GenerateRequest):
    session=sessions.get(req.session_id)
    if not session:
        return {"error": "Invalid session_id"}

    result = generate_frd(session["context"], session["answers"])

    session["generated_frd"] = result

    return result

@app.post("/score")
def score(req: ScoreRequest):
    session=sessions.get(req.session_id)
    if not session:     
        return {"error": "Invalid session_id"}  
         
    frd = session.get("generated_frd", {})

    if not frd:
        return {"error": "No FRD found. Generate first."}

    frd_text = frd.get("frd_text", "")

    result = score_frd(frd_text)

    session["health_score"] = result

    return result