#!/usr/bin/env python3
"""Refresh backend/tests/fixtures/*_reviews.json from live App Store feeds."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.fetch import fetch_reviews

FIXTURES = Path(__file__).resolve().parents[1] / "tests" / "fixtures"
APPS = [
    ("6743496454", False, 40),
    ("6502638001", False, 40),
    ("544007664", True, 30),
]


def main() -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    for app_id, us_only, limit in APPS:
        if app_id == "6743496454":
            src = Path(__file__).resolve().parents[1] / "data" / "cookshelf_reviews.json"
            reviews = json.loads(src.read_text(encoding="utf-8"))[:limit]
        else:
            reviews = fetch_reviews(
                app_id, us_only=us_only, sleep_between_countries=0
            )[:limit]
        path = FIXTURES / f"{app_id}_reviews.json"
        path.write_text(json.dumps(reviews, indent=2), encoding="utf-8")
        print(f"Wrote {path} ({len(reviews)} reviews)")


if __name__ == "__main__":
    main()
