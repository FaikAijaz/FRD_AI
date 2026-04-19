import uuid
from fastapi import FastAPI
from dotenv import load_dotenv

from app.models import DocumentRequest, AnswerRequest, GenerateRequest, ScoreRequest
from app.assessment import assess_document
from app.clarification import generate_question
from app.generation import generate_frd
from app.scoring import score_frd

# In-memory session store
sessions = {}

load_dotenv()
app = FastAPI(title="AI FRD Intelligence Engine")


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
        "session_id": session_id,
        "question": question
    }


@app.post("/answer")
def answer_question(req: AnswerRequest):
    session = sessions.get(req.session_id)

    if not session:
        return {"error": "Invalid session_id"}

    session["answers"].append(req.answer)
    session["question_count"] += 1

    # Stop after 5 questions
    if session["question_count"] >= 5:
        return {
            "done": True,
            "message": "Enough information collected. Ready for FRD generation."
        }

    combined_context = session["context"] + "\n" + "\n".join(session["answers"])

    next_question = generate_question(combined_context, session["missing"])

    return {
        "done": False,
        "question": next_question
    }


@app.post("/generate")
def generate(req: GenerateRequest):
    session = sessions.get(req.session_id)

    if not session:
        return {"error": "Invalid session_id"}

    result = generate_frd(session["context"], session["answers"])

    session["generated_frd"] = result

    return result


@app.post("/score")
def score(req: ScoreRequest):
    session = sessions.get(req.session_id)

    if not session:
        return {"error": "Invalid session_id"}

    frd = session.get("generated_frd", {})

    if not frd:
        return {"error": "No FRD found. Generate first."}

    frd_text = frd.get("frd_text", "")

    result = score_frd(frd_text)

    session["health_score"] = result

    return result