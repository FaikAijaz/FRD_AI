from fastapi import FastAPI
from dotenv import load_dotenv
import os
from app.assessment import assess_document
from pydantic import BaseModel
from app.clarification import generate_question
from app.generation import generate_frd
from app.scoring import score_frd

# Temporary in-memory session (simple version)
session_data = {}

load_dotenv()
app = FastAPI(title="AI FRDs Intelligence Engine")

class DocumentRequest(BaseModel):
    text: str

@app.post("/assess")
def assess(req: DocumentRequest):
    result = assess_document(req.text)
    return result

@app.post("/start_clarification")
def start_clarification(req: DocumentRequest):
    assessment = assess_document(req.text)

    session_data["context"] = req.text
    session_data["missing"] = assessment.get("missing_sections", [])
    session_data["answers"] = []
    session_data["question_count"] = 0

    question = generate_question(req.text, session_data["missing"])

    session_data["current_question"] = question

    return {
        "question": question
    }

class AnswerRequest(BaseModel):
    answer: str


@app.post("/answer")
def answer_question(req: AnswerRequest):
    session_data["answers"].append(req.answer)
    session_data["question_count"] += 1

    # Stop condition
    if session_data["question_count"] >= 5:
        return {"message": "Enough information collected. Ready for FRD generation."}

    combined_context = session_data["context"] + "\n".join(session_data["answers"])

    next_question = generate_question(combined_context, session_data["missing"])

    session_data["current_question"] = next_question

    return {
        "question": next_question
    }

@app.post("/generate")
def generate():
    context = session_data.get("context", "")
    answers = session_data.get("answers", [])

    result = generate_frd(context, answers)

    session_data["generated_frd"] = result

    return result

@app.post("/score")
def score():
    frd = session_data.get("generated_frd", {})

    if not frd:
        return {"error": "No FRD found. Generate first."}

    frd_text = frd.get("frd_text", "")

    result = score_frd(frd_text)

    session_data["health_score"] = result

    return result