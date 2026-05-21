"""LLM-based review-to-theme assignment with sentiment awareness."""

from __future__ import annotations

import json
from typing import Any, Callable

from .llm import CLASSIFICATION_BATCH_SIZE, complete_json_many, llm_configured

ProgressFn = Callable[[str], None] | None

_CLASSIFY_SYSTEM = (
    "You classify App Store reviews into predefined product themes. "
    "LOVE themes: assign a review only if the reviewer praises that "
    "specific feature or capability. "
    "PAIN themes: assign a review only if the reviewer complains about "
    "that specific issue. "
    "Do not assign based on keyword overlap alone — read overall sentiment "
    "toward the feature. "
    "A review may belong to multiple themes when it discusses multiple features. "
    "Use exact author and storefront values from the input."
)

_CLASSIFY_RETRY_SUFFIX = (
    " Assign every review that clearly praises or criticizes a listed theme. "
    "Do not leave obvious matches unassigned."
)

_ASSIGNMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "assignments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "theme_key": {"type": "string"},
                    "author": {"type": "string"},
                    "storefront": {"type": "string"},
                },
                "required": ["theme_key", "author", "storefront"],
            },
        }
    },
    "required": ["assignments"],
}


def _review_key(review: dict[str, Any]) -> tuple[str, str]:
    return (
        review.get("author_name") or "Anonymous",
        (review.get("storefront") or "?").lower(),
    )


def merge_assignments(
    llm_matched: dict[str, list[dict[str, Any]]] | None,
    heuristic_matched: dict[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    """Union LLM and keyword hits per theme key."""
    merged: dict[str, list[dict[str, Any]]] = {
        key: list(heuristic_matched.get(key, [])) for key in heuristic_matched
    }
    if not llm_matched:
        return merged

    for key, reviews in llm_matched.items():
        if key not in merged:
            merged[key] = []
        seen = {_review_key(r) for r in merged[key]}
        for review in reviews:
            rk = _review_key(review)
            if rk not in seen:
                merged[key].append(review)
                seen.add(rk)
    return merged


def _apply_assignments(
    data: dict[str, Any] | None,
    *,
    valid_keys: set[str],
    by_key: dict[tuple[str, str], dict[str, Any]],
    matched: dict[str, list[dict[str, Any]]],
) -> None:
    if not data:
        return
    for item in data.get("assignments", []):
        theme_key = item.get("theme_key")
        if theme_key not in valid_keys:
            continue
        review = by_key.get((item.get("author", ""), item.get("storefront", "").lower()))
        if review and review not in matched[theme_key]:
            matched[theme_key].append(review)


def classify_reviews_with_llm(
    reviews: list[dict[str, Any]],
    theme_rules: list[tuple[str, str, bool, list[str]]],
    *,
    on_progress: ProgressFn = None,
    retry_on_empty: bool = True,
) -> dict[str, list[dict[str, Any]]]:
    """Assign reviews to themes using Claude sentiment analysis."""
    if not llm_configured():
        return {key: [] for key, _, _, _ in theme_rules}

    themes = [
        {
            "key": key,
            "title": title,
            "type": "love" if positive else "pain",
        }
        for key, title, positive, _patterns in theme_rules
    ]

    by_key = {_review_key(r): r for r in reviews}
    matched: dict[str, list[dict[str, Any]]] = {key: [] for key, _, _, _ in theme_rules}
    batches: list[list[dict[str, Any]]] = [
        reviews[offset : offset + CLASSIFICATION_BATCH_SIZE]
        for offset in range(0, len(reviews), CLASSIFICATION_BATCH_SIZE)
    ]
    total_batches = len(batches)
    valid_keys = {key for key, _, _, _ in theme_rules}

    def _build_requests(extra_instruction: str = "") -> list[dict[str, Any]]:
        system = _CLASSIFY_SYSTEM + extra_instruction
        requests = []
        for batch in batches:
            payload = [
                {
                    "author": r.get("author_name") or "Anonymous",
                    "storefront": (r.get("storefront") or "?").lower(),
                    "rating": r.get("rating"),
                    "title": r.get("title") or "",
                    "text": r.get("text") or "",
                }
                for r in batch
            ]
            requests.append(
                {
                    "system": system,
                    "user": json.dumps({"themes": themes, "reviews": payload}, ensure_ascii=False),
                    "tool_name": "theme_assignments",
                    "schema": _ASSIGNMENT_SCHEMA,
                }
            )
        return requests

    for extra in ("", _CLASSIFY_RETRY_SUFFIX if retry_on_empty else ""):
        if extra and any(matched.values()):
            break
        if extra:
            matched = {key: [] for key, _, _, _ in theme_rules}

        requests = _build_requests(extra)
        if on_progress:
            on_progress(
                f"Classifying review sentiment… (0/{total_batches} batches)"
                if total_batches > 1
                else "Classifying review sentiment…"
            )

        completed = 0
        for _batch_idx, data in enumerate(complete_json_many(requests)):
            completed += 1
            if on_progress:
                on_progress(
                    f"Classifying review sentiment… ({completed}/{total_batches} batches)"
                    if total_batches > 1
                    else "Classifying review sentiment…"
                )
            _apply_assignments(
                data, valid_keys=valid_keys, by_key=by_key, matched=matched
            )

        if any(matched.values()):
            break

    return matched
