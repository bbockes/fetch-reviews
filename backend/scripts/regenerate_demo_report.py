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
    print(f"Wrote {REPORT_PATH} ({len(result.loves)} loves, {len(result.pain_points)} pains)")


if __name__ == "__main__":
    main()
