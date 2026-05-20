#!/usr/bin/env python3
"""Fetch up to 500 App Store reviews as JSON for a given app URL or ID.

Fetches the US storefront first (up to 500 written reviews). If fewer than 500 are
available, continues with other country storefronts (up to 500 each) until the
global cap is reached or all storefronts are exhausted.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import Any

MAX_PAGES = 10
REVIEWS_PER_PAGE = 50
MAX_REVIEWS = 500
FEED_URL = (
    "https://itunes.apple.com/{country}/rss/customerreviews"
    "/page={page}/id={app_id}/sortby=mostrecent/json"
)

# US is always fetched first; remaining codes run only if the global cap isn't met.
OTHER_COUNTRIES = (
    "gb",
    "ca",
    "au",
    "ie",
    "nz",
    "in",
    "sg",
    "za",
    "ph",
    "mx",
    "br",
    "de",
    "fr",
    "it",
    "es",
    "nl",
    "be",
    "at",
    "ch",
    "se",
    "no",
    "dk",
    "fi",
    "pl",
    "pt",
    "jp",
    "kr",
    "hk",
    "tw",
    "ae",
    "sa",
    "il",
    "tr",
    "ru",
    "ar",
    "cl",
    "co",
)

APP_ID_PATTERNS = (
    re.compile(r"/id(\d+)", re.I),
    re.compile(r"[?&]id=(\d+)", re.I),
    re.compile(r"^(\d+)$"),
)


def parse_app_id(value: str) -> str:
    value = value.strip()
    for pattern in APP_ID_PATTERNS:
        match = pattern.search(value)
        if match:
            return match.group(1)
    raise ValueError(f"Could not find App Store app ID in: {value!r}")


def label(entry: dict[str, Any], key: str) -> str | None:
    node = entry.get(key)
    if not isinstance(node, dict):
        return None
    label_value = node.get("label")
    return str(label_value) if label_value is not None else None


def normalize_review(
    entry: dict[str, Any], app_id: str, storefront: str
) -> dict[str, Any] | None:
    if "im:rating" not in entry or "content" not in entry:
        return None

    review_id = label(entry, "id")
    if not review_id:
        return None

    rating_raw = label(entry, "im:rating")
    try:
        rating = int(rating_raw) if rating_raw is not None else None
    except ValueError:
        rating = None

    link_node = entry.get("link")
    review_url = None
    if isinstance(link_node, dict):
        attrs = link_node.get("attributes")
        if isinstance(attrs, dict):
            review_url = attrs.get("href")

    author_node = entry.get("author")
    author_uri = None
    author_name = None
    if isinstance(author_node, dict):
        uri_node = author_node.get("uri")
        if isinstance(uri_node, dict):
            author_uri = uri_node.get("label")
        name_node = author_node.get("name")
        if isinstance(name_node, dict):
            author_name = name_node.get("label")

    return {
        "id": review_id,
        "app_id": app_id,
        "storefront": storefront,
        "author_name": author_name,
        "author_uri": author_uri,
        "title": label(entry, "title"),
        "text": label(entry, "content"),
        "rating": rating,
        "version": label(entry, "im:version"),
        "updated": label(entry, "updated"),
        "vote_sum": int(v) if (v := label(entry, "im:voteSum")) is not None and v.isdigit() else None,
        "vote_count": int(v) if (v := label(entry, "im:voteCount")) is not None and v.isdigit() else None,
        "review_url": review_url,
    }


def _load_json_url(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "fetch_reviews/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.URLError as exc:
        if "CERTIFICATE_VERIFY_FAILED" not in str(exc):
            raise
        result = subprocess.run(
            ["curl", "-sL", "-A", "fetch_reviews/1.0", url],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise urllib.error.URLError(result.stderr.strip() or f"curl exit {result.returncode}") from exc
        return json.loads(result.stdout)


def fetch_page(app_id: str, country: str, page: int) -> list[dict[str, Any]]:
    url = FEED_URL.format(country=country, page=page, app_id=app_id)
    try:
        payload = _load_json_url(url)
    except urllib.error.HTTPError as exc:
        if exc.code == 400 and page > 1:
            return []
        raise
    except json.JSONDecodeError as exc:
        raise urllib.error.URLError(f"Invalid JSON from {url}") from exc

    feed = payload.get("feed")
    if not isinstance(feed, dict):
        return []

    entries = feed.get("entry")
    if entries is None:
        return []
    if not isinstance(entries, list):
        entries = [entries]

    reviews: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        normalized = normalize_review(entry, app_id, country)
        if normalized:
            reviews.append(normalized)
    return reviews


def fetch_storefront_reviews(
    app_id: str,
    country: str,
    *,
    max_pages: int = MAX_PAGES,
    global_cap: int = MAX_REVIEWS,
    existing_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Fetch up to max_pages from one storefront, respecting global_cap new reviews."""
    existing_ids = existing_ids or set()
    new_reviews: list[dict[str, Any]] = []

    for page in range(1, max_pages + 1):
        if len(existing_ids) + len(new_reviews) >= global_cap:
            break

        page_reviews = fetch_page(app_id, country, page)
        if not page_reviews:
            break

        for review in page_reviews:
            if review["id"] in existing_ids:
                continue
            if len(existing_ids) + len(new_reviews) >= global_cap:
                break
            new_reviews.append(review)

        if len(page_reviews) < REVIEWS_PER_PAGE:
            break

    return new_reviews


def fetch_reviews(
    app_id: str,
    *,
    max_reviews: int = MAX_REVIEWS,
    us_only: bool = False,
    sleep_between_countries: float = 1.0,
    verbose: bool = True,
) -> list[dict[str, Any]]:
    """US first, then other storefronts until max_reviews or all storefronts exhausted."""
    by_id: dict[str, dict[str, Any]] = {}
    countries = ["us"] if us_only else ["us", *OTHER_COUNTRIES]

    for country in countries:
        if len(by_id) >= max_reviews:
            break

        if verbose:
            print(f"Fetching {country.upper()}…", file=sys.stderr)

        batch = fetch_storefront_reviews(
            app_id,
            country,
            global_cap=max_reviews,
            existing_ids=set(by_id),
        )
        for review in batch:
            by_id[review["id"]] = review

        if verbose:
            added = len(batch)
            print(
                f"  +{added} new ({len(by_id)} total)",
                file=sys.stderr,
            )

        if us_only or len(by_id) >= max_reviews:
            break

        if country != countries[-1] and sleep_between_countries > 0:
            time.sleep(sleep_between_countries)

    return list(by_id.values())


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch up to 500 App Store written reviews as JSON. "
            "US storefront first; other countries if needed to reach the cap."
        )
    )
    parser.add_argument(
        "app",
        help="App Store URL or numeric app ID (e.g. https://apps.apple.com/us/app/.../id123456789)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Write JSON array to this file (default: stdout)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON",
    )
    parser.add_argument(
        "--us-only",
        action="store_true",
        help="Only fetch the US storefront (no multi-country fallback)",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=MAX_REVIEWS,
        metavar="N",
        help=f"Stop after N unique reviews (default: {MAX_REVIEWS})",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=1.0,
        metavar="SEC",
        help="Seconds to wait between country requests when using multi-country (default: 1)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress messages",
    )
    args = parser.parse_args()

    if args.max < 1:
        print("--max must be at least 1", file=sys.stderr)
        return 1

    try:
        app_id = parse_app_id(args.app)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    try:
        reviews = fetch_reviews(
            app_id,
            max_reviews=args.max,
            us_only=args.us_only,
            sleep_between_countries=args.sleep,
            verbose=not args.quiet,
        )
    except urllib.error.URLError as exc:
        print(f"Failed to fetch reviews: {exc}", file=sys.stderr)
        return 1

    indent = 2 if args.pretty else None
    output = json.dumps(reviews, ensure_ascii=False, indent=indent) + "\n"

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(output)
        scope = "US" if args.us_only else "all storefronts"
        print(f"Wrote {len(reviews)} reviews ({scope}) to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
