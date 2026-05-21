"""Review sampling helpers for LLM analysis."""

from __future__ import annotations

from typing import Any


def min_mentions(total_reviews: int) -> int:
    """Minimum reviews required to surface a theme."""
    if total_reviews < 25:
        return 1
    if total_reviews < 80:
        return 2
    return 2


def _review_length(review: dict[str, Any]) -> int:
    return len((review.get("text") or "") + (review.get("title") or ""))


def _rating_bucket(rating: int | None) -> str:
    if rating is None:
        return "mid"
    if rating <= 1:
        return "low"
    if rating <= 3:
        return "mid"
    return "high"


def stratified_review_sample(
    reviews: list[dict[str, Any]],
    *,
    limit: int = 60,
) -> list[dict[str, Any]]:
    """Sample reviews across star ratings so complaints and praise both appear."""
    if len(reviews) <= limit:
        return list(reviews)

    buckets: dict[str, list[dict[str, Any]]] = {"low": [], "mid": [], "high": []}
    for review in reviews:
        buckets[_rating_bucket(review.get("rating"))].append(review)

    for key in buckets:
        buckets[key].sort(key=_review_length, reverse=True)

    present = [k for k in ("low", "mid", "high") if buckets[k]]
    if not present:
        return sorted(reviews, key=_review_length, reverse=True)[:limit]

    per_bucket = max(1, limit // len(present))
    remainder = limit - per_bucket * len(present)
    selected: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    def take_from(bucket_key: str, count: int) -> None:
        nonlocal selected
        for review in buckets[bucket_key]:
            if len(selected) >= limit:
                return
            rid = review.get("id") or id(review)
            if rid in seen_ids:
                continue
            seen_ids.add(rid)
            selected.append(review)
            count -= 1
            if count <= 0:
                return

    for i, key in enumerate(present):
        extra = 1 if i < remainder else 0
        take_from(key, per_bucket + extra)

    if len(selected) < limit:
        for review in sorted(reviews, key=_review_length, reverse=True):
            if len(selected) >= limit:
                break
            rid = review.get("id") or id(review)
            if rid not in seen_ids:
                seen_ids.add(rid)
                selected.append(review)

    return selected[:limit]


def review_to_sample_payload(review: dict[str, Any], *, max_chars: int = 480) -> dict[str, Any]:
    title = (review.get("title") or "").strip()
    text = (review.get("text") or "").strip()
    combined = f"{title}\n\n{text}".strip() if title and text else text or title
    if len(combined) > max_chars:
        combined = combined[: max_chars - 1].rsplit(" ", 1)[0] + "…"
    return {
        "author": review.get("author_name") or "Anonymous",
        "storefront": (review.get("storefront") or "?").lower(),
        "rating": review.get("rating"),
        "text": combined,
    }


def sample_payloads(
    reviews: list[dict[str, Any]],
    *,
    limit: int = 60,
) -> list[dict[str, Any]]:
    sampled = stratified_review_sample(reviews, limit=limit)
    return [review_to_sample_payload(r) for r in sampled]
