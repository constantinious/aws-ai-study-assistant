from fastapi import APIRouter, Depends

from app.middleware.auth import get_current_user
from app.models.progress import UserProgressSummary
from app.services.progress import get_summary

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("", response_model=UserProgressSummary)
def get_progress(user_id: str = Depends(get_current_user)) -> UserProgressSummary:
    """Return the authenticated user's progress across all AIF-C01 domains."""
    return get_summary(user_id)
