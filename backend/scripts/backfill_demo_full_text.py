#!/usr/bin/env python3
"""Add full_text to each quote in cookshelf_demo_report.json from bundled reviews."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.analyze import _review_body
from app.demo_data import REPORT_PATH, REVIEWS_PATH
from app.models import Quote, ReportResult, Theme


def _quote_key(quote: Quote) -> tuple[str, str]:
    return (quote.author.strip().lower(), quote.storefront.strip().upper())


def _review_lookup(reviews: list[dict]) -> dict[tuple[str, str], str]:
    lookup: dict[tuple[str, str], str] = {}
    for review in reviews:
        author = (review.get("author_name") or "").strip().lower()
        storefront = (review.get("storefront") or "?").strip().upper()
        if author:
            lookup[(author, storefront)] = _review_body(review)
    return lookup


def _backfill_theme(theme: Theme, lookup: dict[tuple[str, str], str]) -> Theme:
    quotes: list[Quote] = []
    for quote in theme.quotes:
        full = lookup.get(_quote_key(quote), "").strip()
        if full and full != quote.full_text:
            quotes.append(quote.model_copy(update={"full_text": full}))
        else:
            quotes.append(quote)
    return theme.model_copy(update={"quotes": quotes})


def main() -> None:
    if not REPORT_PATH.exists():
        raise SystemExit(f"Missing {REPORT_PATH}")

    reviews = json.loads(REVIEWS_PATH.read_text(encoding="utf-8"))
    lookup = _review_lookup(reviews)
    report = ReportResult.model_validate_json(REPORT_PATH.read_text(encoding="utf-8"))

    loves = [_backfill_theme(t, lookup) for t in report.loves]
    pains = [_backfill_theme(t, lookup) for t in report.pain_points]
    updated = report.model_copy(update={"loves": loves, "pain_points": pains})

    REPORT_PATH.write_text(updated.model_dump_json(indent=2), encoding="utf-8")
    matched = sum(
        1
        for theme in updated.loves + updated.pain_points
        for quote in theme.quotes
        if quote.full_text.strip()
    )
    total = sum(len(t.quotes) for t in updated.loves + updated.pain_points)
    print(f"Wrote {REPORT_PATH} — full_text on {matched}/{total} quotes")


if __name__ == "__main__":
    main()
