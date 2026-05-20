#!/usr/bin/env python3
"""Regenerate backend/data/cookshelf_demo_report.json from bundled reviews."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from app.analyze import analyze_heuristic
from app.demo_data import COOKSHELF_APP_ID, COOKSHELF_APP_NAME, REPORT_PATH, REVIEWS_PATH


def main() -> None:
    reviews = json.loads(REVIEWS_PATH.read_text(encoding="utf-8"))
    result = analyze_heuristic(reviews, COOKSHELF_APP_ID, COOKSHELF_APP_NAME)
    REPORT_PATH.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    print(f"Wrote {REPORT_PATH} ({len(result.loves)} loves, {len(result.pain_points)} pains)")


if __name__ == "__main__":
    main()
