from datetime import datetime

from pydantic import BaseModel

from app.models.domain import ExamDomain


class DomainProgress(BaseModel):
    domain: ExamDomain
    domain_label: str
    correct_count: int = 0
    total_count: int = 0
    accuracy: float = 0.0
    last_answered_at: datetime | None = None


class HistoryEntry(BaseModel):
    question_id: str
    domain: ExamDomain
    correct: bool
    answered_at: datetime


class UserProgressSummary(BaseModel):
    domains: list[DomainProgress]
    overall_accuracy: float
    total_answered: int
    current_streak: int
    recent_history: list[HistoryEntry] = []
