"""LLM-based review-to-theme assignment with sentiment awareness."""

from __future__ import annotations

import json
import os
from typing import Any


def _review_key(review: dict[str, Any]) -> tuple[str, str]:
    return (
        review.get("author_name") or "Anonymous",
        (review.get("storefront") or "?").lower(),
    )


def classify_reviews_with_llm(
    reviews: list[dict[str, Any]],
    theme_rules: list[tuple[str, str, bool, list[str]]],
) -> dict[str, list[dict[str, Any]]] | None:
    """Assign reviews to themes using LLM sentiment analysis.

    Returns None when no API key is configured or the call fails.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        return None

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
    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    batch_size = 25

    for offset in range(0, len(reviews), batch_size):
        batch = reviews[offset : offset + batch_size]
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

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You classify App Store reviews into predefined product themes. "
                        "Return JSON only. "
                        "LOVE themes: assign a review only if the reviewer praises that "
                        "specific feature or capability. "
                        "PAIN themes: assign a review only if the reviewer complains about "
                        "that specific issue. "
                        "Do not assign based on keyword overlap alone — read overall sentiment "
                        "toward the feature. "
                        "Example: mentioning a 'cookbook collection' while complaining books "
                        "are missing is a PAIN about indexing, not LOVE about large collections. "
                        "A review may belong to multiple themes when it discusses multiple features. "
                        "Use exact author and storefront values from the input."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {"themes": themes, "reviews": payload},
                        ensure_ascii=False,
                    ),
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "theme_assignments",
                    "strict": True,
                    "schema": {
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
                                    "additionalProperties": False,
                                },
                            }
                        },
                        "required": ["assignments"],
                        "additionalProperties": False,
                    },
                },
            },
        )

        raw = response.choices[0].message.content
        if not raw:
            continue

        data = json.loads(raw)
        valid_keys = {key for key, _, _, _ in theme_rules}
        for item in data.get("assignments", []):
            theme_key = item.get("theme_key")
            if theme_key not in valid_keys:
                continue
            review = by_key.get((item.get("author", ""), item.get("storefront", "").lower()))
            if review and review not in matched[theme_key]:
                matched[theme_key].append(review)

    if not any(matched.values()):
        return None

    return matched
