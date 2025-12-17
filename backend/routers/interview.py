from fastapi import APIRouter, HTTPException, status
import uuid
from typing import Dict, Any, List
from backend.ml.generate_questions import generate_interview_questions
from backend.schemas.interview import (
    StartResponse, StartRequest, AnswerRequest,
    FinishRequest, EvaluationDetail, EvaluationResponse
)

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
    details: List[EvaluationDetail] = []
    total = 0.0

    for q in sess["questions"]:
        qid = q.id
        qtext = q.text
        ans = sess["answers"].get(qid, "")

        length_score = min(len(ans.split()) / 40, 1.0) * 6
        keyword_score = 4 if any(
            w.lower() in ans.lower() for w in qtext.split()[:4]
        ) else 0

        score = round(length_score + keyword_score, 2)
        total += score

        details.append(
            EvaluationDetail(
                question_id=qid,
                question=qtext,
                answer=ans,
                score=score,
                feedback=(
                    "Excellent answer"
                    if score >= 8
                    else "Good answer, add more depth"
                    if score >= 5
                    else "Needs improvement"
                ),
            )
        )

    overall = round(total / len(sess["questions"]), 2)

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
