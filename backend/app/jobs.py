from __future__ import annotations

import json
import threading
import uuid
from typing import Any

from .analyze_pipeline import require_llm_configured, run_analysis_pipeline
from .demo_data import load_demo_result
from .errors import AnalysisError
from .fetch import fetch_app_metadata, fetch_reviews, parse_app_id
from .llm import llm_configured
from .models import ReportJob

DEMO_REPORT_ID = "demo"


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, ReportJob] = {}
        self._lock = threading.Lock()
        self._seed_demo_job()

    def _seed_demo_job(self) -> None:
        """Stable CookShelf demo — always available at GET /api/reports/demo."""
        try:
            result = load_demo_result()
        except Exception:
            from .demo_data import _FALLBACK

            result = _FALLBACK
        self._jobs[DEMO_REPORT_ID] = ReportJob(
            id=DEMO_REPORT_ID,
            status="complete",
            progress_message="Demo report ready",
            result=result,
            reviews=None,
        )

    def create(self, app_id: str, *, us_only: bool = False, demo: bool = False) -> str:
        if demo:
            return DEMO_REPORT_ID

        report_id = str(uuid.uuid4())
        job = ReportJob(
            id=report_id,
            status="queued",
            progress_message="Starting…",
        )
        with self._lock:
            self._jobs[report_id] = job

        thread = threading.Thread(
            target=self._run,
            args=(report_id, app_id, us_only),
            daemon=True,
        )
        thread.start()
        return report_id

    def refresh_demo(self) -> None:
        """Reload demo report from disk (fast — never runs full analysis)."""
        with self._lock:
            self._seed_demo_job()

    def get(self, report_id: str) -> ReportJob | None:
        with self._lock:
            if report_id == DEMO_REPORT_ID:
                # Refresh from disk so deploys pick up updated demo JSON
                self._seed_demo_job()
            job = self._jobs.get(report_id)
            return job.model_copy(deep=True) if job else None

    def _update(self, report_id: str, **kwargs: Any) -> None:
        with self._lock:
            job = self._jobs.get(report_id)
            if not job:
                return
            self._jobs[report_id] = job.model_copy(update=kwargs)

    def _run(self, report_id: str, app_id: str, us_only: bool) -> None:
        try:
            if not llm_configured():
                self._update(
                    report_id,
                    status="failed",
                    error="Analysis requires ANTHROPIC_API_KEY. Configure it on the server.",
                )
                return

            self._update(report_id, status="fetching", progress_message="Fetching US reviews…")

            def on_progress(msg: str) -> None:
                self._update(report_id, progress_message=msg)

            reviews = fetch_reviews(
                app_id,
                us_only=us_only,
                sleep_between_countries=0.5 if not us_only else 0,
                on_progress=on_progress,
            )

            if not reviews:
                self._update(
                    report_id,
                    status="failed",
                    error="No written reviews found for this app.",
                )
                return

            self._update(
                report_id,
                status="analyzing",
                progress_message="Looking up app details…",
                reviews=reviews,
            )

            metadata = fetch_app_metadata(app_id)

            self._update(
                report_id,
                status="analyzing",
                progress_message=f"Analyzing {len(reviews)} reviews…",
            )

            def on_analyze_progress(msg: str) -> None:
                self._update(report_id, status="analyzing", progress_message=msg)

            require_llm_configured()
            result = run_analysis_pipeline(
                reviews,
                app_id,
                metadata,
                on_progress=on_analyze_progress,
            )
            self._update(
                report_id,
                status="complete",
                progress_message="Report ready",
                result=result,
                reviews=reviews,
            )
        except AnalysisError as exc:
            self._update(report_id, status="failed", error=str(exc))
        except Exception as exc:  # noqa: BLE001
            self._update(report_id, status="failed", error=str(exc))


job_store = JobStore()
