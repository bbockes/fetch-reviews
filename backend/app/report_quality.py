"""Quality checks before marking a report complete."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import Theme
from .review_sampling import min_mentions


@dataclass
class QualityResult:
    ok: bool
    issues: list[str] = field(default_factory=list)


def _count_by_rating(reviews: list[dict[str, Any]], star: int) -> int:
    return sum(1 for r in reviews if r.get("rating") == star)


def check_report_quality(
    loves: list[Theme],
    pains: list[Theme],
    reviews: list[dict[str, Any]],
) -> QualityResult:
    issues: list[str] = []
    total = len(reviews)
    threshold = min_mentions(total)
    one_star = _count_by_rating(reviews, 1)
    five_star = _count_by_rating(reviews, 5)

    for themes, label in ((loves, "love"), (pains, "pain")):
        for theme in themes:
            if theme.mention_count < threshold:
                issues.append(f"{label}_theme_below_min_mentions:{theme.title}")
            if not theme.quotes:
                issues.append(f"{label}_theme_no_quotes:{theme.title}")

    if total >= 15 and one_star >= 3 and not pains:
        issues.append("no_pain_themes")
    if total >= 15 and five_star >= 5 and not loves:
        issues.append("no_love_themes")

    substantive = sum(
        1 for r in reviews if len((r.get("text") or "") + (r.get("title") or "")) > 40
    )
    if substantive >= 10 and len(loves) + len(pains) < 3:
        issues.append("too_few_themes")

    if not loves and not pains and total >= 5:
        issues.append("empty_themes")

    return QualityResult(ok=len(issues) == 0, issues=issues)
