"""Unit tests for the adaptive domain selection algorithm."""

from collections import Counter

from app.models.domain import ExamDomain
from app.models.progress import DomainProgress
from app.services.adaptive import select_domain


def _make_progress(domain: ExamDomain, correct: int, total: int) -> DomainProgress:
    from app.models.domain import DOMAIN_METADATA

    accuracy = correct / total if total > 0 else 0.0
    return DomainProgress(
        domain=domain,
        domain_label=DOMAIN_METADATA[domain]["label"],
        correct_count=correct,
        total_count=total,
        accuracy=accuracy,
    )


class TestSelectDomain:
    def test_returns_valid_domain_with_no_history(self):
        result = select_domain([])
        assert result in list(ExamDomain)

    def test_no_history_samples_all_domains_over_many_runs(self):
        """With no history, all domains should eventually be selected."""
        seen = set()
        for _ in range(200):
            seen.add(select_domain([]))
        assert len(seen) == len(ExamDomain)

    def test_weak_domain_selected_more_often(self):
        """A domain with 0% accuracy should be selected far more than 100% accuracy domains."""
        progress = [
            _make_progress(ExamDomain.AI_ML_FUNDAMENTALS, 0, 10),       # 0% — weak
            _make_progress(ExamDomain.GENERATIVE_AI_FUNDAMENTALS, 10, 10),  # 100% — strong
            _make_progress(ExamDomain.FOUNDATION_MODELS, 10, 10),        # 100% — strong
            _make_progress(ExamDomain.RESPONSIBLE_AI, 10, 10),           # 100% — strong
            _make_progress(ExamDomain.SECURITY_GOVERNANCE, 10, 10),      # 100% — strong
        ]

        counts: Counter = Counter()
        for _ in range(500):
            counts[select_domain(progress)] += 1

        weak_count = counts[ExamDomain.AI_ML_FUNDAMENTALS]
        strong_total = sum(counts[d] for d in ExamDomain if d != ExamDomain.AI_ML_FUNDAMENTALS)

        # Weak domain should be selected at least 4x more than each strong domain on average
        assert weak_count > strong_total / 4

    def test_unattempted_domain_treated_as_weak(self):
        """A domain with no attempts should be weighted as 0% accuracy."""
        progress = [
            _make_progress(ExamDomain.GENERATIVE_AI_FUNDAMENTALS, 10, 10),
            _make_progress(ExamDomain.FOUNDATION_MODELS, 10, 10),
            _make_progress(ExamDomain.RESPONSIBLE_AI, 10, 10),
            _make_progress(ExamDomain.SECURITY_GOVERNANCE, 10, 10),
            # AI_ML_FUNDAMENTALS is absent — should be treated as weak
        ]

        counts: Counter = Counter()
        for _ in range(300):
            counts[select_domain(progress)] += 1

        # Unattempted domain should appear more than any single strong domain
        assert counts[ExamDomain.AI_ML_FUNDAMENTALS] > counts[ExamDomain.GENERATIVE_AI_FUNDAMENTALS]

    def test_all_domains_can_still_appear_when_one_is_perfect(self):
        """Even 100% accuracy domains should occasionally appear (floor weight)."""
        progress = [_make_progress(d, 10, 10) for d in ExamDomain]

        seen = set()
        for _ in range(500):
            seen.add(select_domain(progress))

        assert len(seen) == len(ExamDomain)
