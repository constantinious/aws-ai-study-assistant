import logging

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError

from app.middleware.auth import get_current_user
from app.models.domain import DOMAIN_METADATA, ExamDomain
from app.models.question import AnswerResult, AnswerSubmission, Question, QuestionResponse
from app.services import adaptive, progress
from app.services.answer_token import decode_answer_token
from app.services.explanation import generate_explanation
from app.services.question_gen import generate_question

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.get("/question", response_model=QuestionResponse)
def get_question(
    domain: ExamDomain | None = None,
    user_id: str = Depends(get_current_user),
) -> QuestionResponse:
    """
    Return a freshly generated AIF-C01 practice question.

    If `domain` is not specified, the adaptive algorithm selects the
    domain where the user needs the most practice.
    """
    if domain is None:
        user_progress = progress.get_progress(user_id)
        domain = adaptive.select_domain(user_progress)

    try:
        question: Question = generate_question(domain)
    except RuntimeError as exc:
        logger.error("Question generation failed for user=%s domain=%s: %s", user_id, domain, exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not generate question, please try again.",
        ) from exc

    return QuestionResponse(
        id=question.id,
        domain=question.domain,
        domain_label=DOMAIN_METADATA[domain]["label"],
        question_text=question.question_text,
        options=question.options,
        answer_token=question.answer_token,
    )


@router.post("/answer", response_model=AnswerResult)
def submit_answer(
    submission: AnswerSubmission,
    user_id: str = Depends(get_current_user),
) -> AnswerResult:
    """
    Submit an answer for a question.

    The `answer_token` from the question response is decoded server-side
    to verify the correct answer without storing state in the database.
    """
    try:
        question_id, correct_index = decode_answer_token(submission.answer_token)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired answer token.",
        ) from exc

    if question_id != submission.question_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answer token does not match question ID.",
        )

    question = Question(
        id=question_id,
        domain=submission.domain,
        question_text=submission.question_text,
        options=submission.options,
        answer_token=submission.answer_token,
    )

    result = generate_explanation(question, submission.selected_index, correct_index)

    progress.record_answer(
        user_id=user_id,
        domain=submission.domain,
        question_id=question_id,
        correct=result.correct,
    )

    return result
