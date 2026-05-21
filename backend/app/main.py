from __future__ import annotations

import os

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .demo_data import COOKSHELF_APP_ID, load_demo_result
from .fetch import parse_app_id
from .jobs import DEMO_REPORT_ID, job_store
from .models import (
    CreateReportRequest,
    CreateReportResponse,
    ParseRequest,
    ParseResponse,
    ReportJob,
)

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
load_dotenv()

app = FastAPI(title="fetch_reviews API", version="0.1.0")

origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/parse", response_model=ParseResponse)
def parse(body: ParseRequest) -> ParseResponse:
    try:
        app_id = parse_app_id(body.input)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ParseResponse(app_id=app_id)


@app.post("/api/reports", response_model=CreateReportResponse)
def create_report(body: CreateReportRequest) -> CreateReportResponse:
    try:
        parse_app_id(body.app_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    report_id = job_store.create(
        body.app_id,
        us_only=body.us_only,
        demo=body.demo,
    )
    return CreateReportResponse(report_id=report_id)


@app.get("/api/reports/demo", response_model=ReportJob)
def get_demo_report() -> ReportJob:
    """CookShelf sample report with full paginated quotes."""
    job = job_store.get(DEMO_REPORT_ID)
    if not job:
        return ReportJob(
            id=DEMO_REPORT_ID,
            status="complete",
            progress_message="Demo report ready",
            result=load_demo_result(),
        )
    return job


@app.get("/api/reports/{report_id}", response_model=ReportJob)
def get_report(report_id: str) -> ReportJob:
    job = job_store.get(report_id)
    if not job:
        raise HTTPException(status_code=404, detail="Report not found")
    return job
