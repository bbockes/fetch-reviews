"""LLM-first analysis orchestrator for any App Store app."""

from __future__ import annotations

from collections import Counter
from typing import Any, Callable

from .analyze import (
    _filter_feature_loves,
    _filter_feature_pains,
    _match_themes_heuristic,
    _reviews_to_quotes,
    _sort_theme_reviews,
    build_review_analysis_one_liner,
)
from .app_context import AppContext, app_context_from_metadata
from .errors import AnalysisError
from .llm import llm_configured
from .models import Quote, ReportResult, ReportSummary, Theme
from .quote_refiner import refine_quotes_for_themes_parallel
from .report_quality import check_report_quality
from .review_sampling import min_mentions
from .takeaway_generator import generate_takeaways_with_llm
from .theme_classifier import classify_reviews_with_llm, merge_assignments
from .theme_discovery import discover_themes_with_llm
from .theme_unified import UNIFIED_REVIEW_LIMIT, extract_themes_unified

ProgressFn = Callable[[str], None] | None

ThemeRule = tuple[str, str, bool, list[str]]


def require_llm_configured() -> None:
    if not llm_configured():
        raise AnalysisError(
            "Analysis requires ANTHROPIC_API_KEY. Configure it on the server."
        )


def _build_themes_from_matched(
    rules: list[ThemeRule],
    matched: dict[str, list[dict[str, Any]]],
    *,
    total_reviews: int,
    on_progress: ProgressFn = None,
) -> tuple[list[Theme], list[Theme]]:
    threshold = min_mentions(total_reviews)
    loves: list[Theme] = []
    pains: list[Theme] = []
    refine_jobs: list[tuple[str, list[Quote]]] = []
    pending: list[tuple[bool, str, int, None]] = []

    for key, title, positive, patterns in rules:
        hits = matched.get(key, [])
        if len(hits) < threshold:
            continue
        sorted_hits = _sort_theme_reviews(hits)
        quotes = _reviews_to_quotes(sorted_hits, patterns=patterns)
        refine_jobs.append((title, quotes))
        pending.append((positive, title, len(hits), None))

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

    loves = _filter_feature_loves(loves)
    loves.sort(key=lambda t: t.mention_count, reverse=True)
    pains = _filter_feature_pains(pains)
    pains.sort(key=lambda t: t.mention_count, reverse=True)
    return loves, pains


def _discover_classify_build(
    reviews: list[dict[str, Any]],
    app_context: AppContext,
    *,
    on_progress: ProgressFn = None,
    retry_hint: str | None = None,
) -> tuple[list[Theme], list[Theme], list[ThemeRule]]:
    rules = discover_themes_with_llm(
        reviews,
        app_context=app_context,
        on_progress=on_progress,
        retry_hint=retry_hint,
    )
    if not rules:
        raise AnalysisError("Theme discovery failed — could not identify themes from reviews.")

    llm_matched = classify_reviews_with_llm(
        reviews, rules, on_progress=on_progress, retry_on_empty=True
    )
    heuristic_matched = _match_themes_heuristic(reviews, rules)
    matched = merge_assignments(llm_matched, heuristic_matched)

    loves, pains = _build_themes_from_matched(
        rules, matched, total_reviews=len(reviews), on_progress=on_progress
    )
    return loves, pains, rules


def run_analysis_pipeline(
    reviews: list[dict[str, Any]],
    app_id: str,
    metadata: dict[str, Any],
    *,
    on_progress: ProgressFn = None,
) -> ReportResult:
    """Full LLM analysis with quality gate and retry."""
    require_llm_configured()

    app_context = app_context_from_metadata(app_id, metadata)
    app_name = app_context.get("app_name")
    app_url = app_context.get("app_url") or f"https://apps.apple.com/us/app/id{app_id}"

    loves: list[Theme] = []
    pains: list[Theme] = []

    if len(reviews) <= UNIFIED_REVIEW_LIMIT:
        unified = extract_themes_unified(
            reviews, app_context=app_context, on_progress=on_progress
        )
        if unified:
            loves, pains = unified
            loves = _filter_feature_loves(loves)
            pains = _filter_feature_pains(pains)

    quality = check_report_quality(loves, pains, reviews)
    if not quality.ok:
        loves, pains, _rules = _discover_classify_build(
            reviews, app_context, on_progress=on_progress
        )
        quality = check_report_quality(loves, pains, reviews)

    if not quality.ok:
        loves, pains, _rules = _discover_classify_build(
            reviews,
            app_context,
            on_progress=on_progress,
            retry_hint="Previous pass missed themes. Issues: " + ", ".join(quality.issues),
        )
        quality = check_report_quality(loves, pains, reviews)

    if not quality.ok:
        raise AnalysisError(
            "Could not extract reliable themes from this review sample. "
            "Try again or use a larger review set."
        )

    ratings = [r["rating"] for r in reviews if r.get("rating") is not None]
    avg = sum(ratings) / len(ratings) if ratings else 0.0
    storefronts = Counter((r.get("storefront") or "?").lower() for r in reviews)
    distribution = Counter(r.get("rating") for r in reviews if r.get("rating"))

    takeaways = generate_takeaways_with_llm(
        loves,
        pains,
        app_name=app_name,
        app_context=app_context,
        reviews=reviews,
        sample_review_count=len(reviews),
        on_progress=on_progress,
    )

    return ReportResult(
        summary=ReportSummary(
            average_rating=round(avg, 2),
            total_reviews=len(reviews),
            one_liner=build_review_analysis_one_liner(len(reviews), len(storefronts)),
            app_id=app_id,
            app_name=app_name,
            app_url=app_url,
            rating_distribution={
                str(k): distribution[k] for k in sorted(distribution, reverse=True)
            },
            storefronts=dict(storefronts),
        ),
        loves=loves[:10],
        pain_points=pains[:10],
        takeaways=takeaways,
    )
