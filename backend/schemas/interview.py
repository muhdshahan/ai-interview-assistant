from pydantic import BaseModel, ConfigDict
from typing import List

class StartRequest(BaseModel):
    job_title: str
    num_questions: int

class Question(BaseModel):
    id: int           # you use string IDs → keep it
    text: str

    model_config = ConfigDict(from_attributes=True)

class StartResponse(BaseModel):
    session_id: str
    num_questions: int
    questions: List[Question]

    model_config = ConfigDict(from_attributes=True)


class AnswerRequest(BaseModel):
    session_id: str
    question_id: int
    answer: str


class FinishRequest(BaseModel):
    session_id: str


class EvaluationDetail(BaseModel):
    question_id: str
    question: str
    answer: str
    score: float
    technical_score: float
    grammar_score: float
    technical_feedback: str
    grammar_suggestions: str

    model_config = ConfigDict(from_attributes=True)  # optional but good


class EvaluationResponse(BaseModel):
    session_id: str
    overall_score: float
    details: List[EvaluationDetail]

    model_config = ConfigDict(from_attributes=True)