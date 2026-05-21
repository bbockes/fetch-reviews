"""Single-call theme extraction for smaller review samples."""

from __future__ import annotations

import json
from typing import Any, Callable

from .analyze import review_lookup
from .app_context import AppContext, app_context_for_prompt
from .llm import complete_json, llm_configured
from .models import Quote, Theme
from .review_sampling import min_mentions, sample_payloads

ProgressFn = Callable[[str], None] | None

_UNIFIED_SYSTEM = (
    "You analyze App Store written reviews for one app and produce a theme report. "
    "Use app genre/description for category-appropriate theme titles. "
    "Each theme must name a specific product capability (praise) or complaint (pain), "
    "not generic enthusiasm or frustration. "
    "Quotes must be verbatim excerpts from the assigned review (1–3 sentences). "
    "Use exact author and storefront from the input."
)

_UNIFIED_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "themes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "title": {"type": "string"},
                    "type": {"type": "string", "enum": ["love", "pain"]},
                    "mention_count": {"type": "integer"},
                    "quotes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "author": {"type": "string"},
                                "storefront": {"type": "string"},
                                "rating": {"type": "integer"},
                                "excerpt": {"type": "string"},
                            },
                            "required": ["author", "storefront", "excerpt"],
                        },
                    },
                },
                "required": ["key", "title", "type", "mention_count", "quotes"],
            },
        }
    },
    "required": ["themes"],
}

UNIFIED_REVIEW_LIMIT = 80


def extract_themes_unified(
    reviews: list[dict[str, Any]],
    *,
    app_context: AppContext,
    on_progress: ProgressFn = None,
) -> tuple[list[Theme], list[Theme]] | None:
    """Return (loves, pains) from one LLM call, or None to fall back to discover+classify."""
    if not llm_configured() or len(reviews) > UNIFIED_REVIEW_LIMIT or len(reviews) < 2:
        return None

    if on_progress:
        on_progress("Extracting themes and quotes…")

    payload = {
        "app_context": app_context_for_prompt(app_context),
        "review_count": len(reviews),
        "min_mentions_per_theme": min_mentions(len(reviews)),
        "reviews": sample_payloads(reviews, limit=60),
    }

    data = complete_json(
        system=_UNIFIED_SYSTEM,
        user=json.dumps(payload, ensure_ascii=False, indent=2),
        tool_name="unified_themes",
        schema=_UNIFIED_SCHEMA,
    )
    if not data:
        return None

    loves: list[Theme] = []
    pains: list[Theme] = []
    floor = min_mentions(len(reviews))
    by_author_storefront = review_lookup(reviews)

    for entry in data.get("themes") or []:
        title = (entry.get("title") or "").strip()
        theme_type = (entry.get("type") or "").lower()
        mention_count = entry.get("mention_count") or 0
        if not title or mention_count < floor:
            continue

        quotes: list[Quote] = []
        for q in entry.get("quotes") or []:
            excerpt = (q.get("excerpt") or "").strip()
            if not excerpt:
                continue
            author = q.get("author") or "Anonymous"
            storefront = (q.get("storefront") or "?").lower()
            full_text = by_author_storefront.get((author, storefront), excerpt)
            quotes.append(
                Quote(
                    author=author,
                    storefront=storefront.upper(),
                    rating=q.get("rating"),
                    text=excerpt,
                    full_text=full_text,
                    highlights=[],
                    excerpt=excerpt[:180] + ("…" if len(excerpt) > 180 else ""),
                )
            )
        if not quotes:
            continue

        theme = Theme(
            mention_count=int(mention_count),
            title=title,
            quotes=quotes[:5],
            also_noted=None,
        )
        if theme_type == "love":
            loves.append(theme)
        elif theme_type == "pain":
            pains.append(theme)

    if not loves and not pains:
        return None

    return loves, pains
