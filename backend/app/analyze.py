"""Theme extraction from reviews — LLM when configured, keyword fallback otherwise."""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from typing import Any

from .models import Quote, ReportResult, ReportSummary, Theme

# Keyword themes for heuristic analysis (works without API key)
THEME_RULES: list[tuple[str, str, bool, list[str]]] = [
    (
        "ingredient_search",
        "Search by ingredient across cookbooks",
        True,
        [
            r"search.{0,40}ingredient",
            r"ingredient.{0,40}search",
            r"search by ingredient",
            r"search across",
            r"reverse search",
        ],
    ),
    (
        "use_cookbooks",
        "Rediscovering neglected cookbooks",
        True,
        [
            r"rediscover",
            r"use my cookbook",
            r"googl",
            r"books on the shelf",
            r"neglected",
        ],
    ),
    (
        "collection_size",
        "Built for large cookbook collections",
        True,
        [
            r"\d+.{0,15}cookbook",
            r"collection",
            r"library of",
            r"hundred",
        ],
    ),
    (
        "grocery",
        "Grocery store & meal planning",
        True,
        [
            r"grocery",
            r"meal plan",
            r"fridge",
            r"at the store",
        ],
    ),
    (
        "enthusiasm",
        "Strong enthusiasm & game changer",
        True,
        [
            r"game.?changer",
            r"love this",
            r"amazing",
            r"best app",
            r"genius",
        ],
    ),
    (
        "pricing",
        "Subscription too expensive",
        False,
        [
            r"\$\d+",
            r"too expensive",
            r"overpriced",
            r"subscription",
            r"per year",
            r"annual",
        ],
    ),
    (
        "one_time",
        "Wants one-time purchase",
        False,
        [
            r"one.?time",
            r"buy once",
            r"rent my book",
            r"pay once",
        ],
    ),
    (
        "missing_books",
        "Cookbooks missing or not indexed",
        False,
        [
            r"not in.{0,20}database",
            r"not indexed",
            r"couldn't find",
            r"missing book",
            r"only \d+ of",
        ],
    ),
    (
        "no_recipes",
        "No full recipe in the app",
        False,
        [
            r"no recipe",
            r"doesn't have the recipe",
            r"only.{0,20}ingredient",
            r"no directions",
            r"no method",
        ],
    ),
    (
        "hidden_price",
        "Pricing not disclosed upfront",
        False,
        [
            r"misleading",
            r"nowhere.{0,30}pay",
            r"before.{0,20}subscription",
            r"upfront",
        ],
    ),
]


def _excerpt(text: str, max_len: int = 180) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rsplit(" ", 1)[0] + "…"


def _match_themes(reviews: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    matched: dict[str, list[dict[str, Any]]] = {rule[0]: [] for rule in THEME_RULES}

    for review in reviews:
        blob = f"{review.get('title', '')} {review.get('text', '')}".lower()
        for key, _title, _positive, patterns in THEME_RULES:
            if any(re.search(p, blob) for p in patterns):
                matched[key].append(review)

    return matched


def _reviews_to_quotes(
    reviews: list[dict[str, Any]], limit: int | None = None
) -> list[Quote]:
    quotes: list[Quote] = []
    subset = reviews if limit is None else reviews[:limit]
    for r in subset:
        text = r.get("text") or ""
        quotes.append(
            Quote(
                author=r.get("author_name") or "Anonymous",
                storefront=(r.get("storefront") or "?").upper(),
                rating=r.get("rating"),
                excerpt=_excerpt(text),
            )
        )
    return quotes


def analyze_heuristic(
    reviews: list[dict[str, Any]], app_id: str, app_name: str | None = None
) -> ReportResult:
    matched = _match_themes(reviews)
    ratings = [r["rating"] for r in reviews if r.get("rating") is not None]
    avg = sum(ratings) / len(ratings) if ratings else 0.0
    storefronts = Counter((r.get("storefront") or "?").lower() for r in reviews)
    distribution = Counter(r.get("rating") for r in reviews if r.get("rating"))

    loves: list[Theme] = []
    pains: list[Theme] = []

    for key, title, positive, _patterns in THEME_RULES:
        hits = matched[key]
        if len(hits) < 2:
            continue
        sorted_hits = sorted(
            hits, key=lambda r: r.get("rating") or 0, reverse=positive
        )
        quotes = _reviews_to_quotes(sorted_hits)
        theme = Theme(
            mention_count=len(hits),
            title=title,
            quotes=quotes,
            also_noted=None,
        )
        if positive:
            loves.append(theme)
        else:
            pains.append(theme)

    loves.sort(key=lambda t: t.mention_count, reverse=True)
    pains.sort(key=lambda t: t.mention_count, reverse=True)

    if not loves and reviews:
        top_positive = sorted(
            [r for r in reviews if (r.get("rating") or 0) >= 4],
            key=lambda r: len(r.get("text") or ""),
            reverse=True,
        )[:8]
        if top_positive:
            loves.append(
                Theme(
                    mention_count=len(top_positive),
                    title="What delighted reviewers",
                    quotes=_reviews_to_quotes(top_positive),
                )
            )

    if not pains and reviews:
        top_negative = sorted(
            [r for r in reviews if (r.get("rating") or 5) <= 3],
            key=lambda r: len(r.get("text") or ""),
            reverse=True,
        )[:8]
        if top_negative:
            pains.append(
                Theme(
                    mention_count=len(top_negative),
                    title="Common complaints",
                    quotes=_reviews_to_quotes(top_negative),
                )
            )

    one_liner = (
        f"Analyzed {len(reviews)} written reviews (avg {avg:.2f}★). "
        f"{len(loves)} positive themes and {len(pains)} pain points surfaced."
    )

    takeaways = [
        "Lead with your strongest praise themes in marketing and onboarding.",
        "Address top pain points explicitly — many come from mismatched expectations.",
        "Show review count and data sources so buyers trust the sample size.",
    ]
    if avg < 4:
        takeaways.insert(
            0,
            "Average rating is below 4★ — prioritize fixing the highest-volume complaints.",
        )

    return ReportResult(
        summary=ReportSummary(
            average_rating=round(avg, 2),
            total_reviews=len(reviews),
            one_liner=one_liner,
            app_id=app_id,
            app_name=app_name,
            app_url=f"https://apps.apple.com/us/app/id{app_id}",
            rating_distribution={str(k): distribution[k] for k in sorted(distribution, reverse=True)},
            storefronts=dict(storefronts),
        ),
        loves=loves[:10],
        pain_points=pains[:10],
        takeaways=takeaways,
    )


def analyze_with_llm(
    reviews: list[dict[str, Any]], app_id: str, app_name: str | None = None
) -> ReportResult | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        return None

    compact = []
    for r in reviews[:120]:
        compact.append(
            {
                "author": r.get("author_name"),
                "storefront": r.get("storefront"),
                "rating": r.get("rating"),
                "title": r.get("title"),
                "text": _excerpt(r.get("text") or "", 400),
            }
        )

    schema = {
        "type": "object",
        "properties": {
            "summary": {
                "type": "object",
                "properties": {
                    "one_liner": {"type": "string"},
                },
                "required": ["one_liner"],
            },
            "loves": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "mention_count": {"type": "integer"},
                        "title": {"type": "string"},
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
                        "also_noted": {"type": "string"},
                    },
                    "required": ["mention_count", "title", "quotes"],
                },
            },
            "pain_points": {"$ref": "#/properties/loves"},
            "takeaways": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["summary", "loves", "pain_points", "takeaways"],
    }

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {
                "role": "system",
                "content": (
                    "You analyze App Store written reviews. Return JSON only. "
                    "Rank themes by mention_count. mention_count must equal the number of "
                    "unique reviews represented in quotes. Include a short verbatim excerpt "
                    "for every review that supports each theme. "
                    "Themes should be specific product insights, not generic praise."
                ),
            },
            {
                "role": "user",
                "content": json.dumps({"app_id": app_id, "reviews": compact}),
            },
        ],
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    if not raw:
        return None

    data = json.loads(raw)
    ratings = [r["rating"] for r in reviews if r.get("rating") is not None]
    avg = sum(ratings) / len(ratings) if ratings else 0.0
    storefronts = Counter((r.get("storefront") or "?").lower() for r in reviews)
    distribution = Counter(r.get("rating") for r in reviews if r.get("rating"))

    summary_data = data.get("summary", {})
    loves = [Theme.model_validate(t) for t in data.get("loves", [])]
    pains = [Theme.model_validate(t) for t in data.get("pain_points", [])]
    matched = _match_themes(reviews)
    loves = _enrich_themes_with_review_quotes(loves, matched, positive=True)
    pains = _enrich_themes_with_review_quotes(pains, matched, positive=False)

    return ReportResult(
        summary=ReportSummary(
            average_rating=round(avg, 2),
            total_reviews=len(reviews),
            one_liner=summary_data.get("one_liner", ""),
            app_id=app_id,
            app_name=app_name,
            app_url=f"https://apps.apple.com/us/app/id{app_id}",
            rating_distribution={str(k): distribution[k] for k in sorted(distribution, reverse=True)},
            storefronts=dict(storefronts),
        ),
        loves=loves,
        pain_points=pains,
        takeaways=data.get("takeaways", []),
    )


def _theme_rule_overlap(theme_title: str, rule_title: str) -> int:
    a = set(re.findall(r"[a-z0-9]+", theme_title.lower()))
    b = set(re.findall(r"[a-z0-9]+", rule_title.lower()))
    stop = {"a", "an", "the", "for", "and", "or", "to", "in", "on", "of", "vs"}
    return len((a - stop) & (b - stop))


def _enrich_themes_with_review_quotes(
    themes: list[Theme],
    matched: dict[str, list[dict[str, Any]]],
    *,
    positive: bool,
) -> list[Theme]:
    """Attach full quote lists from raw reviews so mention_count matches quotes."""
    rules = [(key, title, pos) for key, title, pos, _ in THEME_RULES if pos == positive]
    used_keys: set[str] = set()
    enriched: list[Theme] = []

    for theme in themes:
        best_key: str | None = None
        best_score = 0
        for key, rule_title, _ in rules:
            if key in used_keys:
                continue
            score = _theme_rule_overlap(theme.title, rule_title)
            if score > best_score:
                best_score = score
                best_key = key

        if best_key and best_score > 0:
            used_keys.add(best_key)
            hits = matched.get(best_key, [])
            if hits:
                sorted_hits = sorted(
                    hits,
                    key=lambda r: r.get("rating") or 0,
                    reverse=positive,
                )
                quotes = _reviews_to_quotes(sorted_hits)
                enriched.append(
                    theme.model_copy(
                        update={
                            "mention_count": len(hits),
                            "quotes": quotes,
                            "also_noted": None,
                        }
                    )
                )
                continue

        enriched.append(theme)

    return enriched


def analyze_reviews(
    reviews: list[dict[str, Any]], app_id: str, app_name: str | None = None
) -> ReportResult:
    llm_result = analyze_with_llm(reviews, app_id, app_name)
    if llm_result:
        return llm_result
    return analyze_heuristic(reviews, app_id, app_name)
