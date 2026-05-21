#!/usr/bin/env python3
"""Regenerate backend/data/cookshelf_demo_report.json from bundled reviews."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from app.demo_data import REPORT_PATH, build_demo_report_from_reviews


def main() -> None:
    result = build_demo_report_from_reviews()
    by_cat = {c: 0 for c in ("strength", "fix", "opportunity")}
    for t in result.takeaways:
        by_cat[t.category] = by_cat.get(t.category, 0) + 1
    print(
        f"Wrote {REPORT_PATH} ({len(result.loves)} loves, {len(result.pain_points)} pains, "
        f"{len(result.takeaways)} takeaways: {by_cat['strength']} strength / "
        f"{by_cat['fix']} fix / {by_cat['opportunity']} opportunity)"
    )


if __name__ == "__main__":
    main()
