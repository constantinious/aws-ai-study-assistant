from pydantic import BaseModel, Field

from app.models.domain import ExamDomain


class Question(BaseModel):
    id: str
    domain: ExamDomain
    question_text: str
    options: list[str] = Field(..., min_length=4, max_length=4)
    # Signed token embedding the correct index — never sent to the client raw
    answer_token: str


class QuestionResponse(BaseModel):
    """Public-facing question (no answer embedded)."""

    id: str
    domain: ExamDomain
    domain_label: str
    question_text: str
    options: list[str]
    answer_token: str


class AnswerSubmission(BaseModel):
    question_id: str
    answer_token: str
    selected_index: int = Field(..., ge=0, le=3)
    # Echo back from the question response so the server can generate explanations
    domain: ExamDomain
    question_text: str
    options: list[str] = Field(..., min_length=4, max_length=4)


class SourceCitation(BaseModel):
    text: str
    source: str


class AnswerResult(BaseModel):
    question_id: str
    correct: bool
    correct_index: int
    selected_index: int
    explanation: str
    citations: list[SourceCitation] = []
