"""CookShelf demo — pre-baked report with full quote lists for pagination."""

from __future__ import annotations

import json
from pathlib import Path

from .analyze import analyze_reviews
from .models import Quote, ReportResult, ReportSummary, Theme

COOKSHELF_APP_ID = "6743496454"
COOKSHELF_APP_NAME = "CookShelf: Search Cookbooks"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REVIEWS_PATH = DATA_DIR / "cookshelf_reviews.json"
REPORT_PATH = DATA_DIR / "cookshelf_demo_report.json"

_FALLBACK = ReportResult(
    summary=ReportSummary(
        average_rating=3.69,
        total_reviews=89,
        one_liner="Analyzed 89 written reviews from the App Store spread across 5 Countries.",
        app_id=COOKSHELF_APP_ID,
        app_name=COOKSHELF_APP_NAME,
        app_url="https://apps.apple.com/us/app/cookshelf-search-cookbooks/id6743496454",
        rating_distribution={"5": 38, "4": 6, "3": 17, "2": 6, "1": 22},
        storefronts={"us": 63, "gb": 14, "ca": 7, "au": 2, "nz": 3},
    ),
    loves=[
        Theme(
            mention_count=1,
            title="Search by ingredient across cookbooks",
            quotes=[
                Quote(
                    author="plumberful",
                    storefront="US",
                    rating=5,
                    text="Being able to search by ingredients is a game-changer.",
                    excerpt="Being able to search by ingredients is a game-changer.",
                ),
            ],
        ),
    ],
    pain_points=[],
    takeaways=["Populate backend/data/cookshelf_demo_report.json for the full demo."],
)


def load_demo_result() -> ReportResult:
    if REPORT_PATH.exists():
        return ReportResult.model_validate_json(REPORT_PATH.read_text(encoding="utf-8"))

    if REVIEWS_PATH.exists():
        reviews = json.loads(REVIEWS_PATH.read_text(encoding="utf-8"))
        result = analyze_reviews(reviews, COOKSHELF_APP_ID, COOKSHELF_APP_NAME)
        REPORT_PATH.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        return result

    return _FALLBACK
