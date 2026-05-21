"""Theme extraction from reviews — LLM when configured, keyword fallback otherwise."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Callable

from .llm import llm_configured
from .models import Quote, QuoteHighlight, ReportResult, ReportSummary, Theme
from .quote_refiner import refine_quotes_for_themes_parallel

ProgressFn = Callable[[str], None] | None


def build_review_analysis_one_liner(review_count: int, country_count: int) -> str:
    """Hero summary copy — keep in sync with web/lib/report-utils reviewAnalysisSummary."""
    country_word = "Country" if country_count == 1 else "Countries"
    review_phrase = f"{review_count} written reviews"
    source = "App Store"
    region_phrase = f"{country_count} {country_word}"
    return f"Analyzed {review_phrase} from the {source} spread across {region_phrase}."


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
            r"\d+\+?\s*(?:odd\s+)?cookbooks?",
            r"\d+.{0,15}cookbook",
            r"(?:large|huge|big|massive|extensive|enormous).{0,20}(?:collection|library)",
            r"(?:collection|library).{0,20}(?:cookbook|cookbooks)",
            r"too many cookbooks",
            r"many cookbooks",
            r"hundred.{0,15}cookbook",
            r"cookbook.{0,15}addiction",
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
        "barcode_add",
        "Add cookbooks by scanning barcodes",
        True,
        [
            r"bar.?code",
            r"scanning",
            r"scan the",
            r"scan your",
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
            r"not.{0,12}indexed",
            r"couldn't find",
            r"could not find",
            r"missing book",
            r"missing from",
            r"only \d+ of",
            r"weren't on",
            r"wasn't on",
            r"not on the app",
            r"books weren",
            r"library lacking",
            r"library needs",
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


GENERIC_LOVE_TITLE_RE = re.compile(
    r"enthusiasm|game.?changer|generic praise|what delighted|overall love|"
    r"amazing app|best app|love this app|users love|strong praise",
    re.I,
)

GENERIC_PAIN_TITLE_RE = re.compile(
    r"common complaint|generic|overall hate|terrible app|hate this app|"
    r"worst app|users hate|strong complaint|overall frustration|what hurts",
    re.I,
)


def _is_feature_love_theme(title: str) -> bool:
    """Exclude generic enthusiasm — praise themes must name a product capability."""
    return not GENERIC_LOVE_TITLE_RE.search(title)


def _is_feature_pain_theme(title: str) -> bool:
    """Exclude generic frustration — pain themes must name a product capability."""
    return not GENERIC_PAIN_TITLE_RE.search(title)


def _filter_feature_loves(loves: list[Theme]) -> list[Theme]:
    return [theme for theme in loves if _is_feature_love_theme(theme.title)]


def _filter_feature_pains(pains: list[Theme]) -> list[Theme]:
    return [theme for theme in pains if _is_feature_pain_theme(theme.title)]


def _sort_theme_reviews(reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank quotes by substance, not star rating."""
    return sorted(reviews, key=lambda r: len(r.get("text") or ""), reverse=True)


_NEGATIVE_SENTENCE_RE = re.compile(
    r"\b("
    r"not|no|never|none|nothing|missing|lack|lacking|without|unfortunately|sadly|"
    r"disappoint|disappointed|frustrat|incentive|defeat|waste|confus|pointless|"
    r"useless|terrible|awful|horrible|worst|hate|loathe|can't|cannot|won't|"
    r"couldn't|could not|wasn't|was not|weren't|were not|isn't|is not|aren't|are not|"
    r"doesn't|does not|don't|do not|didn't|did not"
    r")\b",
    re.I,
)

_POSITIVE_SENTENCE_RE = re.compile(
    r"\b("
    r"love|loved|great|amazing|perfect|helpful|useful|worth|recommend|excellent|"
    r"fantastic|finally|best|wonderful|awesome|brilliant|fabulous|joy|favorite|"
    r"favourite|glad|happy|excited|impressed|game.?changer"
    r")\b",
    re.I,
)


def _review_blob(review: dict[str, Any]) -> str:
    return f"{review.get('title', '')} {review.get('text', '')}"


def _sentence_bounds(text: str, position: int) -> tuple[int, int]:
    start = max(text.rfind(".", 0, position), text.rfind("!", 0, position))
    start = max(start, text.rfind("?", 0, position), text.rfind("\n", 0, position))
    start = 0 if start < 0 else start + 1

    end_candidates = [text.find(ch, position) for ch in ".!?\n"]
    end_candidates = [idx for idx in end_candidates if idx >= 0]
    end = min(end_candidates) + 1 if end_candidates else len(text)
    return start, end


def _pattern_matches_in_context(
    review: dict[str, Any],
    patterns: list[str],
    *,
    positive: bool,
) -> bool:
    body = _review_blob(review)
    rating = review.get("rating")

    for pattern in patterns:
        try:
            matches = list(re.finditer(pattern, body, re.I))
        except re.error:
            continue
        if not matches:
            continue

        for match in matches:
            sent_start, sent_end = _sentence_bounds(body, match.start())
            sentence = body[sent_start:sent_end]
            has_negative = bool(_NEGATIVE_SENTENCE_RE.search(sentence))
            has_positive = bool(_POSITIVE_SENTENCE_RE.search(sentence))

            if positive:
                if has_negative and not has_positive:
                    continue
                if rating is not None and rating <= 2:
                    continue
                if rating == 3 and has_negative:
                    continue
                return True
            else:
                if has_negative:
                    return True
                if rating is not None and rating <= 3 and not has_positive:
                    return True
                if rating is not None and rating <= 2:
                    return True

        if not positive and rating is not None and rating <= 2:
            return True

    return False


def _match_themes_heuristic(reviews: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    matched: dict[str, list[dict[str, Any]]] = {rule[0]: [] for rule in THEME_RULES}

    for review in reviews:
        for key, _title, positive, patterns in THEME_RULES:
            if _pattern_matches_in_context(review, patterns, positive=positive):
                matched[key].append(review)

    return matched


def _match_themes(
    reviews: list[dict[str, Any]],
    *,
    on_progress: ProgressFn = None,
) -> dict[str, list[dict[str, Any]]]:
    from .theme_classifier import classify_reviews_with_llm

    llm_matched = classify_reviews_with_llm(reviews, THEME_RULES, on_progress=on_progress)
    if llm_matched:
        return llm_matched
    return _match_themes_heuristic(reviews)


def _excerpt(text: str, max_len: int = 180) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rsplit(" ", 1)[0] + "…"


def _review_body(review: dict[str, Any]) -> str:
    title = (review.get("title") or "").strip()
    text = (review.get("text") or "").strip()
    if title and text:
        if text.lower().startswith(title.lower()):
            return text
        return f"{title}\n\n{text}"
    return text or title


def _merge_spans(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not spans:
        return []
    spans = sorted(spans)
    merged = [spans[0]]
    for start, end in spans[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def _highlight_spans(text: str, patterns: list[str]) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for pattern in patterns:
        try:
            for match in re.finditer(pattern, text, re.I):
                if match.end() > match.start():
                    spans.append((match.start(), match.end()))
        except re.error:
            continue
    return _merge_spans(spans)


def _reviews_to_quotes(
    reviews: list[dict[str, Any]],
    *,
    patterns: list[str] | None = None,
    theme_title: str | None = None,
    limit: int | None = None,
) -> list[Quote]:
    quotes: list[Quote] = []
    subset = reviews if limit is None else reviews[:limit]
    for r in subset:
        body = _review_body(r)
        highlight_spans = _highlight_spans(body, patterns) if patterns else []
        quotes.append(
            Quote(
                author=r.get("author_name") or "Anonymous",
                storefront=(r.get("storefront") or "?").upper(),
                rating=r.get("rating"),
                text=body,
                full_text=body,
                highlights=[
                    QuoteHighlight(start=start, end=end) for start, end in highlight_spans
                ],
                excerpt=_excerpt(body),
            )
        )

    if theme_title and quotes:
        quotes = refine_quotes_for_theme(quotes, theme_title)

    return quotes


def analyze_heuristic(
    reviews: list[dict[str, Any]],
    app_id: str,
    app_name: str | None = None,
    *,
    on_progress: ProgressFn = None,
) -> ReportResult:
    matched = _match_themes(reviews, on_progress=on_progress)
    ratings = [r["rating"] for r in reviews if r.get("rating") is not None]
    avg = sum(ratings) / len(ratings) if ratings else 0.0
    storefronts = Counter((r.get("storefront") or "?").lower() for r in reviews)
    distribution = Counter(r.get("rating") for r in reviews if r.get("rating"))

    loves: list[Theme] = []
    pains: list[Theme] = []
    refine_jobs: list[tuple[str, list[Quote]]] = []
    pending: list[tuple[bool, str, int, list[Quote] | None]] = []
    use_llm_quotes = llm_configured()

    for key, title, positive, patterns in THEME_RULES:
        hits = matched[key]
        if len(hits) < 2:
            continue
        sorted_hits = _sort_theme_reviews(hits)
        if use_llm_quotes:
            quotes = _reviews_to_quotes(sorted_hits, patterns=patterns)
            refine_jobs.append((title, quotes))
            pending.append((positive, title, len(hits), None))
        else:
            quotes = _reviews_to_quotes(sorted_hits, patterns=patterns, theme_title=title)
            pending.append((positive, title, len(hits), quotes))

    if refine_jobs:
        if on_progress:
            on_progress("Extracting theme quotes…")
        refined_by_title = refine_quotes_for_themes_parallel(refine_jobs)
        for i, (positive, title, mention_count, _) in enumerate(pending):
            quotes = refined_by_title.get(title, refine_jobs[i][1])
            theme = Theme(
                mention_count=mention_count,
                title=title,
                quotes=quotes,
                also_noted=None,
            )
            if positive:
                loves.append(theme)
            else:
                pains.append(theme)
    else:
        for positive, title, mention_count, quotes in pending:
            if quotes is None:
                continue
            theme = Theme(
                mention_count=mention_count,
                title=title,
                quotes=quotes,
                also_noted=None,
            )
            if positive:
                loves.append(theme)
            else:
                pains.append(theme)

    loves = _filter_feature_loves(loves)
    loves.sort(key=lambda t: t.mention_count, reverse=True)
    pains = _filter_feature_pains(pains)
    pains.sort(key=lambda t: t.mention_count, reverse=True)

    one_liner = build_review_analysis_one_liner(len(reviews), len(storefronts))

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


def analyze_reviews(
    reviews: list[dict[str, Any]],
    app_id: str,
    app_name: str | None = None,
    *,
    on_progress: ProgressFn = None,
) -> ReportResult:
    return analyze_heuristic(reviews, app_id, app_name, on_progress=on_progress)
