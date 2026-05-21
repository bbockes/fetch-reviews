"""Discover app-specific love/pain themes from reviews via LLM."""

from __future__ import annotations

import json
import re
from typing import Any, Callable

from .theme_filters import is_feature_love_theme, is_feature_pain_theme
from .app_context import AppContext, app_context_for_prompt
from .llm import complete_json, llm_configured
from .review_sampling import min_mentions, sample_payloads

ProgressFn = Callable[[str], None] | None

ThemeRule = tuple[str, str, bool, list[str]]

_DISCOVERY_SYSTEM = (
    "You analyze App Store written reviews for one mobile app and propose themes "
    "for a product report. Use the app genre and description to choose vocabulary "
    "appropriate to the category (games, productivity, finance, health, etc.). "
    "LOVE themes name a specific capability reviewers praise (not generic enthusiasm). "
    "PAIN themes name a specific complaint (not vague frustration). "
    "Titles are short product-facing phrases (under ~8 words). "
    "Keys are snake_case identifiers. "
    "Keywords are 2–5 short literal phrases reviewers use (for search), not regex. "
    "Prefer concrete features over meta themes like 'great app'."
)

_DISCOVERY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "loves": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "title": {"type": "string"},
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["key", "title", "keywords"],
            },
        },
        "pains": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "title": {"type": "string"},
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["key", "title", "keywords"],
            },
        },
    },
    "required": ["loves", "pains"],
}


def _keywords_to_patterns(keywords: list[str]) -> list[str]:
    patterns: list[str] = []
    for raw in keywords:
        phrase = (raw or "").strip()
        if len(phrase) < 2:
            continue
        if re.search(r"[\\^$.|?*+()\[\]{}]", phrase):
            patterns.append(phrase)
        else:
            escaped = re.escape(phrase)
            patterns.append(escaped.replace(r"\ ", r"\s+"))
    return patterns


def _entries_to_rules(entries: list[dict[str, Any]], *, positive: bool) -> list[ThemeRule]:
    rules: list[ThemeRule] = []
    seen_keys: set[str] = set()
    for entry in entries:
        key = re.sub(r"[^a-z0-9_]+", "_", (entry.get("key") or "").strip().lower())
        key = key.strip("_")
        title = (entry.get("title") or "").strip()
        if not key or not title or key in seen_keys:
            continue
        if positive and not is_feature_love_theme(title):
            continue
        if not positive and not is_feature_pain_theme(title):
            continue
        seen_keys.add(key)
        keywords = entry.get("keywords") or []
        if not isinstance(keywords, list):
            keywords = []
        patterns = _keywords_to_patterns([str(k) for k in keywords])
        rules.append((key, title, positive, patterns))
    return rules


def _count_by_rating(reviews: list[dict[str, Any]], star: int) -> int:
    return sum(1 for r in reviews if r.get("rating") == star)


def validate_theme_rules(
    rules: list[ThemeRule],
    reviews: list[dict[str, Any]],
) -> bool:
    if not rules:
        return False
    loves = [r for r in rules if r[2]]
    pains = [r for r in rules if not r[2]]
    keys = [r[0] for r in rules]
    if len(keys) != len(set(keys)):
        return False

    total = len(reviews)
    if total >= 15:
        if _count_by_rating(reviews, 1) >= 3 and not pains:
            return False
        if _count_by_rating(reviews, 5) >= 5 and not loves:
            return False
    return bool(loves or pains)


def discover_themes_with_llm(
    reviews: list[dict[str, Any]],
    *,
    app_context: AppContext | None = None,
    on_progress: ProgressFn = None,
    retry_hint: str | None = None,
) -> list[ThemeRule] | None:
    """Return theme rules tailored to this app's reviews, or None if discovery fails."""
    if not llm_configured() or len(reviews) < 2:
        return None

    if on_progress:
        on_progress("Discovering themes from reviews…")

    ctx = app_context or AppContext()
    mention_floor = min_mentions(len(reviews))
    review_samples = sample_payloads(reviews, limit=60)

    base_user: dict[str, Any] = {
        "app_context": app_context_for_prompt(ctx),
        "review_count": len(reviews),
        "reviews": review_samples,
        "min_mentions_per_theme": mention_floor,
        "targets": {
            "loves": "4–8 praise themes",
            "pains": "4–8 complaint themes",
        },
    }
    if retry_hint:
        base_user["retry_guidance"] = retry_hint

    attempts = [
        base_user,
        {
            **base_user,
            "retry_guidance": (
                retry_hint
                or "Previous themes missed clear praise or complaints. "
                "Propose more granular, feature-specific themes. "
                "Include at least 3 love and 2 pain themes when reviews support them."
            ),
        },
    ]

    for attempt_user in attempts:
        data = complete_json(
            system=_DISCOVERY_SYSTEM,
            user=json.dumps(attempt_user, ensure_ascii=False, indent=2),
            tool_name="discovered_themes",
            schema=_DISCOVERY_SCHEMA,
        )
        if not data:
            continue

        rules: list[ThemeRule] = []
        rules.extend(_entries_to_rules(data.get("loves") or [], positive=True))
        rules.extend(_entries_to_rules(data.get("pains") or [], positive=False))

        if rules and validate_theme_rules(rules, reviews):
            return rules

    return None
