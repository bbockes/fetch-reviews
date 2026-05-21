from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


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


TakeawayCategory = Literal["strength", "fix", "opportunity"]


class Takeaway(BaseModel):
    title: str
    body: str = ""
    summary: str | None = None
    points: list[str] = Field(default_factory=list)
    category: TakeawayCategory

    @field_validator("body", mode="before")
    @classmethod
    def _default_body(cls, value: Any) -> str:
        return value or ""

    def model_post_init(self, __context: Any) -> None:
        if not self.body and self.summary:
            parts = [self.summary, *self.points]
            object.__setattr__(self, "body", " ".join(p.strip() for p in parts if p.strip()))


class ReportResult(BaseModel):
    summary: ReportSummary
    loves: list[Theme]
    pain_points: list[Theme]
    takeaways: list[Takeaway]

    @field_validator("takeaways", mode="before")
    @classmethod
    def _coerce_legacy_takeaways(cls, value: Any) -> Any:
        """Accept legacy string takeaways (title — body) from older report JSON."""
        if not value:
            return []
        if isinstance(value, list) and value and isinstance(value[0], str):
            return [_legacy_takeaway_from_string(item) for item in value]
        return value


def _legacy_takeaway_from_string(text: str) -> dict[str, str]:
    """Best-effort category guess for pre-structured takeaway strings."""
    dash = text.find(" \u2014 ")
    if dash == -1:
        dash = text.find(" — ")
    title = text[:dash].strip() if dash != -1 else text.strip()
    body = text[dash + 3 :].strip() if dash != -1 else ""
    lower = text.lower()
    if any(
        w in lower
        for w in (
            "fix",
            "complaint",
            "expensive",
            "missing",
            "subscription",
            "screenshot",
            "upfront",
            "paywall",
        )
    ) and not any(w in lower for w in ("lead your", "lead with", "ask for a review", "praise")):
        category = "fix"
    elif any(
        w in lower
        for w in ("lead your", "marketing", "ask for a review", "highlight", "ingredient search")
    ):
        category = "strength"
    else:
        category = "opportunity"
    return {"title": title, "body": body or title, "category": category}


class ReportJob(BaseModel):
    id: str
    status: Literal["queued", "fetching", "analyzing", "complete", "failed"]
    progress_message: str | None = None
    error: str | None = None
    result: ReportResult | None = None
    reviews: list[dict[str, Any]] | None = None
