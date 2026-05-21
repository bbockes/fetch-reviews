"""LLM-generated strategic takeaways — separate call after theme extraction."""

from __future__ import annotations

import json
from typing import Any, Callable

from .llm import complete_json, llm_configured
from .models import Theme

ProgressFn = Callable[[str], None] | None

# Exported so you can inspect or tune the prompt without digging through call sites.
TAKEAWAY_SYSTEM_PROMPT = """You write the "Strategic takeaways" section of a customer review report.

Audience: an indie developer or small team improving their own product. They are NOT professional
product managers. Write in plain, direct language — no jargon (no "sprint", "UVP", "funnel",
"ASO", "cohort", "retention lever", etc.).

Input: themes extracted from a written-review sample (what users love + pain points), with
mention counts and short quote excerpts. Your job is to turn that evidence into exactly 6
actionable recommendations.

Rules:
1. Each takeaway has a short "title" (the call to action) and a "body" (1–3 sentences: why,
   grounded in the themes and mention counts).
2. Titles must state what to DO in plain language — e.g. "Make your subscription less expensive",
   not "Fix subscription too expensive" or quoted theme labels. Tailor every title and body to
   THIS product's themes; never use fill-in-the-blank templates.
3. Be specific: name the actual feature, complaint, or copy change implied by the themes.
4. Do NOT tell them to "improve your rating", "get above 4 stars", or reference the sample's
   average star rating. The written-review sample is incomplete (≤500 reviews) and is NOT the
   product's public rating on any store or marketplace.
5. Do NOT make grandiose or vague claims (e.g. "harder for competitors to copy").
6. Stay platform-agnostic: do NOT name Apple App Store, Google Play, or other specific stores.
   Say "marketing copy", "your product page", "your listing", "screenshots", "before signup",
   or "before download" instead of "App Store description", "Play Store listing", etc.
   Reviews may come from any source; recommendations should work for web apps, mobile apps,
   SaaS, and marketplaces alike.
7. Cover a spread of practical actions when the data supports it, such as:
   - Marketing copy / positioning using top praise themes
   - When to ask for a review (tied to a specific loved moment in the product)
   - The highest-impact product fix for the top pain theme
   - Setting honest expectations in screenshots or listing copy for a top pain
   - Improving the most-mentioned strength (concrete ideas, not "double down")
   - Whether the top praise and top pain might be the same workflow and one fix could help both
8. Use mention counts from the input when relevant. Say "in this sample" or "reviewers here"
   so it is clear you mean this dataset, not all customers everywhere.
9. Bodies must start with a capital letter. No markdown."""

_TAKEAWAY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "takeaways": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["title", "body"],
            },
        }
    },
    "required": ["takeaways"],
}


def build_takeaway_user_prompt(
    *,
    loves: list[Theme],
    pains: list[Theme],
    app_name: str | None,
    sample_review_count: int,
) -> str:
    """Build the user message sent with TAKEAWAY_SYSTEM_PROMPT."""

    def _theme_payload(themes: list[Theme], limit: int = 5) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for theme in themes[:limit]:
            excerpts: list[str] = []
            for quote in theme.quotes[:2]:
                text = (quote.excerpt or quote.text or "").strip()
                if text:
                    excerpts.append(text[:220])
            out.append(
                {
                    "title": theme.title,
                    "mention_count": theme.mention_count,
                    "example_excerpts": excerpts,
                }
            )
        return out

    payload = {
        "app_name": app_name or "Unknown app",
        "written_review_sample_size": sample_review_count,
        "important_context": (
            "This report only includes written reviews from the fetched sample "
            f"({sample_review_count} reviews). It may omit ratings without text. Do not recommend "
            "actions based on the sample average star rating. Do not assume a specific app store "
            "or marketplace — keep recommendations platform-agnostic."
        ),
        "what_users_love": _theme_payload(loves),
        "pain_points": _theme_payload(pains),
        "output": "Return exactly 6 takeaways as JSON.",
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _capitalize_first(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    return text[0].upper() + text[1:]


def _format_takeaway(title: str, body: str) -> str:
    return f"{title.strip()} \u2014 {_capitalize_first(body)}"


def _normalize_takeaways(raw: list[dict[str, Any]]) -> list[str]:
    formatted: list[str] = []
    for item in raw:
        title = (item.get("title") or "").strip()
        body = (item.get("body") or "").strip()
        if title and body:
            formatted.append(_format_takeaway(title, body))
    return formatted[:6]


def _fallback_takeaways(loves: list[Theme], pains: list[Theme]) -> list[str]:
    """Minimal non-LLM fallback when API key is missing or the call fails."""
    items: list[str] = []
    if loves:
        t = loves[0]
        items.append(
            _format_takeaway(
                f"Highlight {t.title.lower()} in your marketing copy",
                f"{t.mention_count} reviewers in this sample praised it. Lead with that benefit "
                f"in your first sentences.",
            )
        )
    if pains:
        t = pains[0]
        items.append(
            _format_takeaway(
                f"Address {t.title.lower()} before adding new features",
                f"{t.mention_count} reviewers in this sample raised it. Fixing this likely "
                f"helps more than another new feature right now.",
            )
        )
    while len(items) < 3:
        items.append(
            _format_takeaway(
                "Re-run this report with an API key for full strategic takeaways",
                "Strategic takeaways are generated by AI from your theme analysis.",
            )
        )
    return items[:6]


def generate_takeaways_with_llm(
    loves: list[Theme],
    pains: list[Theme],
    *,
    app_name: str | None = None,
    sample_review_count: int,
    on_progress: ProgressFn = None,
) -> list[str]:
    """Separate LLM call for strategic takeaways after themes are ready."""
    if not llm_configured():
        return _fallback_takeaways(loves, pains)

    if on_progress:
        on_progress("Generating strategic takeaways…")

    user = build_takeaway_user_prompt(
        loves=loves,
        pains=pains,
        app_name=app_name,
        sample_review_count=sample_review_count,
    )

    data = complete_json(
        system=TAKEAWAY_SYSTEM_PROMPT,
        user=user,
        tool_name="strategic_takeaways",
        schema=_TAKEAWAY_SCHEMA,
    )

    if not data:
        return _fallback_takeaways(loves, pains)

    formatted = _normalize_takeaways(data.get("takeaways", []))
    if len(formatted) < 3:
        return _fallback_takeaways(loves, pains)

    return formatted
