from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ParseRequest(BaseModel):
    input: str


class ParseResponse(BaseModel):
    app_id: str


class CreateReportRequest(BaseModel):
    app_id: str
    us_only: bool = False
    demo: bool = False


class CreateReportResponse(BaseModel):
    report_id: str


class QuoteHighlight(BaseModel):
    start: int
    end: int


class Quote(BaseModel):
    author: str
    storefront: str
    rating: int | None
    text: str = ""
    full_text: str = ""
    highlights: list[QuoteHighlight] = Field(default_factory=list)
    excerpt: str = ""


class Theme(BaseModel):
    mention_count: int
    title: str
    quotes: list[Quote] = Field(default_factory=list)
    also_noted: str | None = None


class ReportSummary(BaseModel):
    average_rating: float
    total_reviews: int
    one_liner: str
    app_id: str
    app_name: str | None = None
    app_url: str | None = None
    rating_distribution: dict[str, int] = Field(default_factory=dict)
    storefronts: dict[str, int] = Field(default_factory=dict)
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class ReportResult(BaseModel):
    summary: ReportSummary
    loves: list[Theme]
    pain_points: list[Theme]
    takeaways: list[str]


class ReportJob(BaseModel):
    id: str
    status: Literal["queued", "fetching", "analyzing", "complete", "failed"]
    progress_message: str | None = None
    error: str | None = None
    result: ReportResult | None = None
    reviews: list[dict[str, Any]] | None = None
