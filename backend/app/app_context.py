"""App metadata from iTunes Lookup for LLM prompts."""

from __future__ import annotations

from typing import Any, TypedDict


class AppContext(TypedDict, total=False):
    app_id: str
    app_name: str | None
    app_url: str | None
    primary_genre: str | None
    genres: list[str]
    description: str | None
    average_user_rating: float | None
    user_rating_count: int | None


def app_context_from_metadata(app_id: str, metadata: dict[str, Any]) -> AppContext:
    return AppContext(
        app_id=app_id,
        app_name=metadata.get("app_name"),
        app_url=metadata.get("app_url"),
        primary_genre=metadata.get("primary_genre"),
        genres=metadata.get("genres") or [],
        description=metadata.get("description"),
        average_user_rating=metadata.get("average_user_rating"),
        user_rating_count=metadata.get("user_rating_count"),
    )


def app_context_for_prompt(ctx: AppContext) -> dict[str, Any]:
    """JSON-serializable subset for LLM user messages."""
    return {
        "app_name": ctx.get("app_name") or "Unknown app",
        "primary_genre": ctx.get("primary_genre"),
        "genres": ctx.get("genres") or [],
        "description": (ctx.get("description") or "")[:500],
        "average_user_rating": ctx.get("average_user_rating"),
        "user_rating_count": ctx.get("user_rating_count"),
    }
