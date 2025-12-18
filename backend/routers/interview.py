from fastapi import APIRouter, HTTPException, status
import uuid
from typing import Dict, Any, List
from backend.ml.generate_questions import generate_interview_questions
from backend.schemas.interview import (
    StartResponse, StartRequest, AnswerRequest,
    FinishRequest, EvaluationDetail, EvaluationResponse
)
from backend.ml.evaluate_answer import score_answer

router = APIRouter(prefix="/interview", tags=["interview"])

_SESSIONS: Dict[str, Dict[str, Any]] = {}

@router.post("/start")
async def start_interview(payload: StartRequest):
    questions = generate_interview_questions(
        payload.job_title, payload.num_questions
    )
    session_id = str(uuid.uuid4())
    _SESSIONS[session_id] = {
        "session_id": session_id,
        "questions": questions,
        "answers": {},
        "finished": False,
        "evaluation": None,
    }
    return StartResponse(
        session_id=session_id,
        num_questions=len(questions),
        questions=questions,
    )


@router.post("/answer")
async def submit_answer(payload: AnswerRequest):
    sess = _SESSIONS.get(payload.session_id)

    if not sess:
        raise HTTPException(404, "Session not found")

    if sess["finished"]:
        raise HTTPException(400, "Interview already finished")

    qids = {q.id for q in sess["questions"]}
    if payload.question_id not in qids:
        raise HTTPException(400, "Invalid question id")

    sess["answers"][payload.question_id] = payload.answer

    return {
        "message": "Answer saved",
        "answered": len(sess["answers"]),
        "total": len(sess["questions"]),
    }

def _evaluate(sess: Dict[str, Any]) -> EvaluationResponse:
    details = []
    total_score = 0.0

    for q in sess["questions"]:
        qid = q.id
        qtext = q.text
        ans = sess["answers"].get(qid, "")

        llm_eval = score_answer(qtext, ans)

        tech = llm_eval["technical_score"]
        gram = llm_eval["grammar_score"]

        question_score = (tech + gram) / 2  # 0–5
        total_score += question_score

        details.append(
            EvaluationDetail(
                question_id=str(qid),
                question=qtext,
                answer=ans,
                score=round(question_score, 2),
                technical_score=tech,
                grammar_score=gram,
                technical_feedback=llm_eval["technical_feedback"],
                grammar_suggestions=llm_eval["grammar_suggestions"],
            )
        )

    overall = round((total_score / len(details)) * 2, 2)  # scale to 10

    return EvaluationResponse(
        session_id=sess["session_id"],
        overall_score=overall,
        details=details,
    )


@router.post("/finish")
async def finish_interview(payload: FinishRequest):
    sess = _SESSIONS.get(payload.session_id)

    if not sess:
        raise HTTPException(404, "Session not found")

    if sess["finished"]:
        return sess["evaluation"]

    if len(sess["answers"]) < len(sess["questions"]):
        raise HTTPException(
            400, "Please answer all questions before finishing"
        )

    result = _evaluate(sess)

    sess["evaluation"] = result
    sess["finished"] = True

    return result

@router.get("/results")
async def get_results(session_id: str):
    sess = _SESSIONS.get(session_id)

    if not sess:
        raise HTTPException(404, "Session not found")

    if not sess["finished"]:
        raise HTTPException(400, "Interview not finished yet")

    return sess["evaluation"]
