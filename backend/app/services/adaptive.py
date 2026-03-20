"""Adaptive domain selection — weight weak domains more heavily."""

import random

from app.models.domain import DOMAIN_METADATA, ExamDomain
from app.models.progress import DomainProgress


def select_domain(progress: list[DomainProgress]) -> ExamDomain:
    """
    Select the next exam domain using weighted random selection.

    Algorithm:
    - For each domain, compute: weight = exam_weight * (1 - accuracy)
    - Domains with lower accuracy get higher weight
    - New users (no attempts) get uniform random selection weighted by exam share
    """
    all_domains = list(ExamDomain)

    if not progress:
        # No history — distribute proportional to exam weight
        weights = [DOMAIN_METADATA[d]["exam_weight"] for d in all_domains]
        return random.choices(all_domains, weights=weights, k=1)[0]

    progress_map = {p.domain: p for p in progress}

    weights = []
    for domain in all_domains:
        exam_weight = DOMAIN_METADATA[domain]["exam_weight"]
        prog = progress_map.get(domain)
        if prog is None or prog.total_count == 0:
            # Never attempted — treat as 0% accuracy (maximum weakness)
            accuracy = 0.0
        else:
            accuracy = prog.accuracy

        # Inverse accuracy: weak domains get more attention
        # +0.05 floor ensures even perfect domains occasionally appear
        weakness = max(1.0 - accuracy, 0.05)
        weights.append(exam_weight * weakness)

    return random.choices(all_domains, weights=weights, k=1)[0]
