"""DynamoDB-backed user progress service."""

import logging
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key

from app.config import settings
from app.models.domain import DOMAIN_METADATA, ExamDomain
from app.models.progress import DomainProgress, HistoryEntry, UserProgressSummary

logger = logging.getLogger(__name__)

_MAX_HISTORY = 50  # entries kept per user


def _table():
    dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
    return dynamodb.Table(settings.dynamodb_table)


def get_progress(user_id: str) -> list[DomainProgress]:
    """Return per-domain progress for a user."""
    table = _table()
    response = table.query(KeyConditionExpression=Key("user_id").eq(user_id))
    items = response.get("Items", [])

    domain_map: dict[ExamDomain, DomainProgress] = {}
    for item in items:
        try:
            domain = ExamDomain(item["domain"])
        except ValueError:
            continue
        domain_map[domain] = DomainProgress(
            domain=domain,
            domain_label=DOMAIN_METADATA[domain]["label"],
            correct_count=int(item.get("correct_count", 0)),
            total_count=int(item.get("total_count", 0)),
            accuracy=float(item.get("accuracy", 0.0)),
            last_answered_at=item.get("last_answered_at"),
        )

    return list(domain_map.values())


def record_answer(user_id: str, domain: ExamDomain, question_id: str, correct: bool) -> DomainProgress:
    """Atomically increment counters and recalculate accuracy."""
    table = _table()
    now = datetime.now(timezone.utc).isoformat()

    correct_delta = 1 if correct else 0

    response = table.update_item(
        Key={"user_id": user_id, "domain": domain.value},
        UpdateExpression=(
            "ADD correct_count :c, total_count :one "
            "SET last_answered_at = :now, accuracy = "
            "  if_not_exists(correct_count, :zero) + :c) / "
            "  (if_not_exists(total_count, :zero) + :one)"
        ),
        ExpressionAttributeValues={
            ":c": correct_delta,
            ":one": 1,
            ":zero": 0,
            ":now": now,
        },
        ReturnValues="ALL_NEW",
    )

    item = response.get("Attributes", {})

    # Recalculate accuracy precisely from returned counters
    total = int(item.get("total_count", 1))
    correct_count = int(item.get("correct_count", 0))
    accuracy = correct_count / total if total > 0 else 0.0

    # Persist the clean accuracy value
    table.update_item(
        Key={"user_id": user_id, "domain": domain.value},
        UpdateExpression="SET accuracy = :acc",
        ExpressionAttributeValues={":acc": round(accuracy, 4)},
    )

    _append_history(table, user_id, question_id, domain, correct, now)

    return DomainProgress(
        domain=domain,
        domain_label=DOMAIN_METADATA[domain]["label"],
        correct_count=correct_count,
        total_count=total,
        accuracy=accuracy,
        last_answered_at=now,
    )


def _append_history(table, user_id: str, question_id: str, domain: ExamDomain, correct: bool, now: str) -> None:
    entry = {
        "question_id": question_id,
        "domain": domain.value,
        "correct": correct,
        "answered_at": now,
    }
    try:
        table.update_item(
            Key={"user_id": user_id, "domain": "history"},
            UpdateExpression=(
                "SET #h = list_append(if_not_exists(#h, :empty), :entry) "
            ),
            ExpressionAttributeNames={"#h": "entries"},
            ExpressionAttributeValues={
                ":entry": [entry],
                ":empty": [],
            },
        )
    except Exception as exc:
        logger.warning("Failed to append history entry: %s", exc)


def get_summary(user_id: str) -> UserProgressSummary:
    """Return a full progress summary including history and streak."""
    domain_progress = get_progress(user_id)

    total_answered = sum(p.total_count for p in domain_progress)
    total_correct = sum(p.correct_count for p in domain_progress)
    overall_accuracy = total_correct / total_answered if total_answered > 0 else 0.0

    history = _get_history(user_id)
    streak = _calculate_streak(history)

    # Ensure all domains appear (even if not yet attempted)
    domain_map = {p.domain: p for p in domain_progress}
    all_domains = [
        domain_map.get(
            d,
            DomainProgress(domain=d, domain_label=DOMAIN_METADATA[d]["label"]),
        )
        for d in ExamDomain
    ]

    return UserProgressSummary(
        domains=all_domains,
        overall_accuracy=round(overall_accuracy, 4),
        total_answered=total_answered,
        current_streak=streak,
        recent_history=history[:20],
    )


def _get_history(user_id: str) -> list[HistoryEntry]:
    table = _table()
    try:
        response = table.get_item(Key={"user_id": user_id, "domain": "history"})
        entries = response.get("Item", {}).get("entries", [])
        history = []
        for e in reversed(entries[-_MAX_HISTORY:]):
            try:
                history.append(
                    HistoryEntry(
                        question_id=e["question_id"],
                        domain=ExamDomain(e["domain"]),
                        correct=e["correct"],
                        answered_at=e["answered_at"],
                    )
                )
            except (ValueError, KeyError):
                continue
        return history
    except Exception as exc:
        logger.warning("Failed to retrieve history: %s", exc)
        return []


def _calculate_streak(history: list[HistoryEntry]) -> int:
    """Count consecutive correct answers from the most recent."""
    streak = 0
    for entry in history:
        if entry.correct:
            streak += 1
        else:
            break
    return streak
