"""LLM-generated strategic takeaways — separate call after theme extraction."""

from __future__ import annotations

import json
import re
from typing import Any, Callable

from .llm import complete_json, llm_configured, takeaway_model
from .models import Takeaway, TakeawayCategory, Theme

ProgressFn = Callable[[str], None] | None

TakeawaysByCategory = dict[TakeawayCategory, list[Takeaway]]

MIN_TAKEAWAYS_PER_CATEGORY = 4
MAX_TAKEAWAYS_PER_CATEGORY = 4

_TAKEAWAY_ITEM_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {
            "type": "string",
            "description": "One short sentence: the core why.",
        },
        "points": {
            "type": "array",
            "items": {"type": "string"},
            "description": "1–3 short supporting sentences with evidence from reviews.",
        },
        "based_on_theme": {
            "type": "string",
            "description": "Exact theme title from the input this recommendation draws on.",
        },
    },
    "required": ["title", "summary", "points", "based_on_theme"],
}

_TAKEAWAY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "strengths": {
            "type": "array",
            "minItems": 4,
            "maxItems": 4,
            "items": _TAKEAWAY_ITEM_SCHEMA,
        },
        "fixes": {
            "type": "array",
            "minItems": 4,
            "maxItems": 4,
            "items": _TAKEAWAY_ITEM_SCHEMA,
        },
        "opportunities": {
            "type": "array",
            "minItems": 4,
            "maxItems": 4,
            "items": _TAKEAWAY_ITEM_SCHEMA,
        },
    },
    "required": ["strengths", "fixes", "opportunities"],
}

_CATEGORY_ORDER: tuple[TakeawayCategory, ...] = ("strength", "fix", "opportunity")

TAKEAWAY_SYSTEM_PROMPT = """You write strategic takeaways for an indie developer who built this product.

You have already read their review themes and sample quotes. Turn that evidence into exactly 12
recommendations: 4 strengths, 4 fixes, 4 opportunities.

Voice: plain, direct, specific — like a sharp friend who read the reviews, not a consultant.
No jargon (sprint, UVP, funnel, ASO, cohort, etc.).

Each item has:
- title: concrete action (imperative, under ~12 words)
- summary: ONE short sentence — the core "why" (under ~25 words)
- points: 1–3 short sentences with evidence (mention counts, quote details). Not a wall of text.
- based_on_theme: exact theme title from the input

Use a different theme for each of the 12 items when possible.

Category guide:
- strengths: Amplify what reviewers praise (visibility, timing a review ask after a win, etc.).
- fixes: Resolve a complaint (price, missing content, surprise after signup).
- opportunities: Connect praise + pain, prioritize one move, or deepen a strength with a
  concrete product idea from the quotes.

Good vs bad:
GOOD title: "Make your subscription less expensive"
BAD title: "Address subscription too expensive"

GOOD summary: "Five reviewers felt blindsided by cost after signup."
GOOD points: ["One only saw the fee after handing over personal info.", "Showing cost earlier would stop that surprise."]
BAD: One long paragraph with no structure.

Hard limits:
- Do NOT name surfaces: no "marketing copy", "website", "listing", "screenshots", "onboarding".
- Do NOT mention average star rating or say "improve your rating".
- Do NOT name App Store, Google Play, or other marketplaces.
- Start summary and each point with a capital letter. No markdown.
- If a quote already ends with a period, do not add another after the closing quote (write 'indexing.' not 'indexing.')."""


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
            for quote in theme.quotes[:3]:
                text = (quote.excerpt or quote.text or "").strip()
                if text:
                    excerpts.append(text[:280])
            out.append(
                {
                    "title": theme.title,
                    "mention_count": theme.mention_count,
                    "example_quotes": excerpts,
                }
            )
        return out

    payload = {
        "app_name": app_name or "Unknown app",
        "written_review_sample_size": sample_review_count,
        "context": (
            f"Sample of {sample_review_count} written reviews only — not the public rating. "
            "Keep recommendations platform-agnostic."
        ),
        "what_users_love": _theme_payload(loves),
        "pain_points": _theme_payload(pains),
        "assignments": {
            "strengths": "Pick 4 different praise themes when possible.",
            "fixes": "Pick 4 different pain themes when possible.",
            "opportunities": "Pick 4 themes; include connections between praise and pain where grounded.",
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _capitalize_first(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    return text[0].upper() + text[1:]


def _ensure_sentence_end(text: str) -> str:
    text = text.strip()
    if text and text[-1] not in ".!?":
        return text + "."
    return text


_QUOTE_PERIOD_DUP = re.compile(r"(['\"])([^'\"]*\.)\1\.")


def _fix_quote_period_duplication(text: str) -> str:
    """Remove a stray period after a closing quote when the quote already ends with one."""
    return _QUOTE_PERIOD_DUP.sub(r"\1\2\1", text)


def _strip_surface_phrases(text: str) -> str:
    out = text
    replacements = [
        (r"\bin your marketing copy\b", ""),
        (r"\bin marketing copy\b", ""),
        (r"\byour marketing copy\b", ""),
        (r"\bon your website\b", ""),
        (r"\bin your listing\b", ""),
        (r"\byour listing\b", ""),
        (r"\bin screenshots\b", ""),
        (r"\bin your screenshots\b", ""),
        (r"\bonboarding ui\b", ""),
        (r"\bonboarding screen\b", ""),
        (r"\bwelcome screen\b", ""),
        (r"\bin onboarding\b", ""),
        (r"\bon your product page\b", ""),
        (r"\bin your first (?:two )?sentences\b", ""),
        (r"\blead your marketing copy with\b", "Highlight"),
        (r"\blead with\b", "Highlight"),
        (r"\blead your\b", "Highlight"),
        (r"\s{2,}", " "),
        (r"\s+\.", "."),
        (r"\s+,", ","),
    ]
    for pattern, repl in replacements:
        out = re.sub(pattern, repl, out, flags=re.I)
    return out.strip(" ,.")


def _compose_body(summary: str, points: list[str]) -> str:
    parts = [_ensure_sentence_end(summary)] if summary.strip() else []
    parts.extend(_ensure_sentence_end(p) for p in points if p.strip())
    return " ".join(parts)


def _sanitize_takeaway(item: Takeaway) -> Takeaway:
    title = _fix_quote_period_duplication(_strip_surface_phrases(item.title))
    summary_raw = item.summary or ""
    summary = _fix_quote_period_duplication(
        _ensure_sentence_end(_capitalize_first(_strip_surface_phrases(summary_raw)))
    )
    points = [
        _fix_quote_period_duplication(
            _ensure_sentence_end(_capitalize_first(_strip_surface_phrases(p)))
        )
        for p in item.points
        if p.strip()
    ]
    if summary or points:
        body = _compose_body(summary, points)
    else:
        body = _fix_quote_period_duplication(
            _ensure_sentence_end(_capitalize_first(_strip_surface_phrases(item.body)))
        )
        summary = summary or None
    return Takeaway(
        title=title,
        body=body,
        summary=summary or None,
        points=points,
        category=item.category,
    )


def _takeaway_full_text(item: Takeaway) -> str:
    if item.summary or item.points:
        return _compose_body(item.summary or "", item.points)
    return item.body


def _normalize_theme_key(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip().lower())


def _theme_mentioned_in_text(theme_title: str, text: str) -> bool:
    key = _normalize_theme_key(theme_title)
    if key in text:
        return True
    shortened = re.sub(r"^(wants|no)\s+", "", key)
    if shortened and shortened in text:
        return True
    tokens = [w for w in re.findall(r"[a-z0-9]+", key) if len(w) > 3]
    if len(tokens) >= 2:
        hits = sum(1 for t in tokens if t in text)
        if hits >= min(2, len(tokens)):
            return True
    return False


def _looks_like_strength_misplaced_in_fix(title: str, text: str, loves: list[Theme]) -> bool:
    lower = text.lower()
    if "highlight" not in lower and "ask for a review" not in lower:
        return False
    if any(w in lower for w in ("expensive", "missing", "paywall", "complaint", "fix ", "upfront")):
        return False
    return any(_theme_mentioned_in_text(t.title, lower) for t in loves)


def _looks_like_fix_misplaced_in_strength(title: str, text: str, pains: list[Theme]) -> bool:
    lower = text.lower()
    if not any(
        w in lower
        for w in ("expensive", "missing", "paywall", "upfront", "before signup", "before sign-up")
    ):
        return False
    return any(_theme_mentioned_in_text(t.title, lower) for t in pains)


def _correct_category_if_obvious(
    item: Takeaway,
    intended: TakeawayCategory,
    *,
    loves: list[Theme],
    pains: list[Theme],
) -> TakeawayCategory:
    text = _takeaway_full_text(item)
    if intended == "fix" and _looks_like_strength_misplaced_in_fix(item.title, text, loves):
        return "strength"
    if intended == "strength" and _looks_like_fix_misplaced_in_strength(
        item.title, text, pains
    ):
        return "fix"
    return intended


def _entry_to_takeaway(
    entry: dict[str, Any],
    category: TakeawayCategory,
    *,
    loves: list[Theme],
    pains: list[Theme],
) -> Takeaway | None:
    title = (entry.get("title") or "").strip()
    summary = _capitalize_first((entry.get("summary") or "").strip())
    raw_points = entry.get("points") or []
    points = [_capitalize_first(str(p).strip()) for p in raw_points if str(p).strip()]
    legacy_body = _capitalize_first((entry.get("body") or "").strip())

    if not title:
        return None
    if not summary and not points and not legacy_body:
        return None

    draft = Takeaway(
        title=title,
        body=legacy_body or _compose_body(summary, points),
        summary=summary or None,
        points=points,
        category=category,
    )
    corrected = _correct_category_if_obvious(draft, category, loves=loves, pains=pains)
    draft.category = corrected
    return _sanitize_takeaway(draft)


def _parse_category_items(
    raw: list[dict[str, Any]] | None,
    category: TakeawayCategory,
    *,
    loves: list[Theme],
    pains: list[Theme],
) -> list[Takeaway]:
    items: list[Takeaway] = []
    for entry in raw or []:
        item = _entry_to_takeaway(entry, category, loves=loves, pains=pains)
        if item:
            items.append(item)
        if len(items) >= MAX_TAKEAWAYS_PER_CATEGORY:
            break
    return items


def _first_excerpt(theme: Theme) -> str:
    for quote in theme.quotes:
        text = (quote.excerpt or quote.text or "").strip()
        if text:
            return text[:120].rsplit(" ", 1)[0] + "…" if len(text) > 120 else text
    return ""


def _feature_label(theme_title: str) -> str:
    key = _normalize_theme_key(theme_title)
    labels = {
        "search by ingredient across cookbooks": "ingredient search across your cookbooks",
        "rediscovering neglected cookbooks": "recipes from cookbooks you already own",
        "built for large cookbook collections": "large cookbook libraries",
        "grocery store & meal planning": "grocery and meal planning",
        "add cookbooks by scanning barcodes": "barcode scanning to add books",
    }
    return labels.get(key, theme_title[0].lower() + theme_title[1:] if theme_title else "")


def _pain_label(theme_title: str) -> str:
    key = _normalize_theme_key(theme_title)
    labels = {
        "subscription too expensive": "subscription cost",
        "wants one-time purchase": "a one-time purchase option",
        "cookbooks missing or not indexed": "missing cookbooks",
        "no full recipe in the app": "recipes not being fully in the app",
        "pricing not disclosed upfront": "pricing",
    }
    return labels.get(key, _feature_label(theme_title))


def _structured_takeaway(
    *,
    title: str,
    summary: str,
    points: list[str],
    category: TakeawayCategory,
) -> Takeaway:
    return _sanitize_takeaway(
        Takeaway(title=title, summary=summary, points=points, body="", category=category)
    )


def _strength_from_love(theme: Theme, *, variant: int) -> Takeaway:
    label = _feature_label(theme.title)
    excerpt = _first_excerpt(theme)
    variants = [
        (
            f"Highlight {label} as a core feature",
            f"{theme.mention_count} reviewers in this sample praise it.",
            [
                f'One wrote: "{excerpt}"' if excerpt else "It is one of the clearest reasons people recommend your product.",
                "That strength is worth emphasizing when you describe what the product does.",
            ],
        ),
        (
            f"Ask for a review after someone uses {label}",
            "That is when satisfaction tends to peak in this sample.",
            [
                f'Reviewers often mention {label} as a win moment{f' — e.g. "{excerpt}"' if excerpt else ""}.',
                "Prompting right then beats a random timer.",
            ],
        ),
        (
            f"Lead with {label} when explaining the product",
            f"It shows up in {theme.mention_count} positive reviews here.",
            [
                "People who want that capability should recognize it immediately.",
                f'Reviewers describe it as a key reason to keep using the app{f' — "{excerpt}"' if excerpt else ""}.',
            ],
        ),
        (
            f"Double down on {label}",
            "This praise theme has more mentions than most others in the sample.",
            [
                f"{theme.mention_count} reviewers tie their enthusiasm to it.",
                "Small improvements here could reinforce what already works.",
            ],
        ),
    ]
    t, s, pts = variants[variant % len(variants)]
    return _structured_takeaway(title=t, summary=s, points=pts[:2], category="strength")


def _fix_from_pain(theme: Theme, *, variant: int) -> Takeaway:
    label = _pain_label(theme.title)
    excerpt = _first_excerpt(theme)
    expensive = "expensive" in theme.title.lower()
    variants = [
        (
            f"Make {label} less of a blocker" if expensive else f"Fix {label} before you ship new features",
            f"{theme.mention_count} reviewers in this sample raised it.",
            [
                f'One example: "{excerpt}"' if excerpt else "It comes up repeatedly in negative reviews.",
                "Tackle this before adding something new.",
            ],
        ),
        (
            f"Be upfront about {label} before people sign up",
            "Several complaints here come from surprise after download.",
            [
                f'A reviewer noted: "{excerpt}"' if excerpt else "People felt misled about what to expect.",
                "Set clear expectations early.",
            ],
        ),
        (
            f"Prioritize {label} in your next release",
            f"This pain theme appears in {theme.mention_count} reviews in the sample.",
            [
                "It blocks people from getting full value from the product.",
                f'Fixing it addresses a complaint users keep repeating{f' — "{excerpt}"' if excerpt else ""}.',
            ],
        ),
        (
            f"Reduce friction around {label}",
            "Users hit this wall often enough that it shapes how they talk about the product.",
            [
                f"{theme.mention_count} reviewers mention it.",
                "Even a partial fix could change the tone of new reviews.",
            ],
        ),
    ]
    t, s, pts = variants[variant % len(variants)]
    return _structured_takeaway(title=t, summary=s, points=pts[:2], category="fix")


def _opportunity_from_themes(
    loves: list[Theme], pains: list[Theme], *, variant: int
) -> Takeaway:
    variants: list[tuple[str, str, list[str]]] = []
    if loves and pains:
        variants.append(
            (
                "Check if your top praise and top complaint happen in the same flow",
                f"Reviewers praise {_feature_label(loves[0].title)} while others complain about {_pain_label(pains[0].title)}.",
                [
                    "One focused change might help critics without hurting what fans already use.",
                    "Look for a single step in that flow where expectations diverge.",
                ],
            )
        )
    if loves:
        excerpt = _first_excerpt(loves[0])
        variants.append(
            (
                f"Make {_feature_label(loves[0].title)} easier to discover",
                f"It shows up in {loves[0].mention_count} reviews here.",
                [
                    f'Reviewers say things like "{excerpt}"' if excerpt else "People only value what they find.",
                    "Surfacing it earlier can turn more users into fans.",
                ],
            )
        )
    if len(loves) >= 2:
        variants.append(
            (
                f"Connect {_feature_label(loves[0].title)} with {_feature_label(loves[1].title)}",
                "Both are praised separately in this sample.",
                [
                    "A workflow that links them could deepen the value people already see.",
                    "Reviewers treat each as a standalone win — combining them may compound retention.",
                ],
            )
        )
    if pains:
        variants.append(
            (
                f"Pick one focused improvement for {_pain_label(pains[0].title)}",
                f"It is among the most-mentioned complaints ({pains[0].mention_count} reviews).",
                [
                    "One concrete fix there may matter more than another feature.",
                    "Ship that before expanding scope elsewhere.",
                ],
            )
        )
    if len(pains) >= 2:
        variants.append(
            (
                f"See if {_pain_label(pains[0].title)} and {_pain_label(pains[1].title)} share a root cause",
                "Both pain themes show up in this sample.",
                [
                    "Fixing one underlying issue might address two complaint clusters at once.",
                    "Group the negative reviews by workflow before picking what to build.",
                ],
            )
        )
    variants.append(
        (
            "Pick one improvement from your most common complaint",
            "The loudest pain themes in this sample point to a clear priority.",
            [
                "Ship a single focused fix before adding anything new.",
                "That is often the fastest way to change how people talk about the product.",
            ],
        )
    )
    t, s, pts = variants[variant % len(variants)]
    return _structured_takeaway(title=t, summary=s, points=pts[:2], category="opportunity")


def _dedupe_takeaways(items: list[Takeaway]) -> list[Takeaway]:
    seen: set[str] = set()
    out: list[Takeaway] = []
    for item in items:
        key = _normalize_theme_key(item.title)
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def _merge_into_bucket(
    target: TakeawaysByCategory,
    category: TakeawayCategory,
    items: list[Takeaway],
) -> None:
    existing = {_normalize_theme_key(t.title) for t in target[category]}
    for item in items:
        if len(target[category]) >= MAX_TAKEAWAYS_PER_CATEGORY:
            break
        key = _normalize_theme_key(item.title)
        if key in existing:
            continue
        target[category].append(_sanitize_takeaway(item))
        existing.add(key)


def _fill_gaps_only(
    grouped: TakeawaysByCategory,
    *,
    loves: list[Theme],
    pains: list[Theme],
) -> TakeawaysByCategory:
    result: TakeawaysByCategory = {
        cat: _dedupe_takeaways(grouped.get(cat, []))[:MAX_TAKEAWAYS_PER_CATEGORY]
        for cat in _CATEGORY_ORDER
    }

    overflow: list[Takeaway] = []
    for category in _CATEGORY_ORDER:
        kept: list[Takeaway] = []
        for item in result[category]:
            corrected = _correct_category_if_obvious(
                item, category, loves=loves, pains=pains
            )
            item = _sanitize_takeaway(
                Takeaway(
                    title=item.title,
                    body=item.body,
                    summary=item.summary,
                    points=item.points,
                    category=corrected,
                )
            )
            if corrected == category and len(kept) < MAX_TAKEAWAYS_PER_CATEGORY:
                kept.append(item)
            else:
                overflow.append(item)
        result[category] = kept

    for item in overflow:
        if len(result[item.category]) < MAX_TAKEAWAYS_PER_CATEGORY:
            _merge_into_bucket(result, item.category, [item])

    def _fill(category: TakeawayCategory, factory) -> None:
        attempts = 0
        slot = 0
        while len(result[category]) < MIN_TAKEAWAYS_PER_CATEGORY and attempts < 16:
            attempts += 1
            candidate = factory(slot)
            slot += 1
            _merge_into_bucket(result, category, [candidate])

    if loves:
        _fill(
            "strength",
            lambda i: _strength_from_love(loves[min(i, len(loves) - 1)], variant=i),
        )
    if pains:
        _fill(
            "fix",
            lambda i: _fix_from_pain(pains[min(i, len(pains) - 1)], variant=i),
        )
    _fill("opportunity", lambda i: _opportunity_from_themes(loves, pains, variant=i))

    return {
        cat: _dedupe_takeaways(result[cat])[:MAX_TAKEAWAYS_PER_CATEGORY]
        for cat in _CATEGORY_ORDER
    }


def _normalize_llm_takeaways(
    data: dict[str, Any],
    *,
    loves: list[Theme],
    pains: list[Theme],
) -> list[Takeaway]:
    grouped: TakeawaysByCategory = {
        "strength": _parse_category_items(
            data.get("strengths"), "strength", loves=loves, pains=pains
        ),
        "fix": _parse_category_items(data.get("fixes"), "fix", loves=loves, pains=pains),
        "opportunity": _parse_category_items(
            data.get("opportunities"), "opportunity", loves=loves, pains=pains
        ),
    }
    grouped = _fill_gaps_only(grouped, loves=loves, pains=pains)
    return flatten_takeaways(grouped)


def flatten_takeaways(grouped: TakeawaysByCategory) -> list[Takeaway]:
    out: list[Takeaway] = []
    for category in _CATEGORY_ORDER:
        out.extend(grouped.get(category, []))
    return out


def group_takeaways(items: list[Takeaway]) -> TakeawaysByCategory:
    grouped: TakeawaysByCategory = {key: [] for key in _CATEGORY_ORDER}
    for item in items:
        grouped[item.category].append(item)
    return grouped


def _fallback_takeaways(loves: list[Theme], pains: list[Theme]) -> list[Takeaway]:
    grouped: TakeawaysByCategory = {"strength": [], "fix": [], "opportunity": []}
    for i in range(MAX_TAKEAWAYS_PER_CATEGORY):
        if loves:
            grouped["strength"].append(
                _strength_from_love(loves[min(i, len(loves) - 1)], variant=i)
            )
        if pains:
            grouped["fix"].append(
                _fix_from_pain(pains[min(i, len(pains) - 1)], variant=i)
            )
        grouped["opportunity"].append(_opportunity_from_themes(loves, pains, variant=i))
    grouped = _fill_gaps_only(grouped, loves=loves, pains=pains)
    return flatten_takeaways(grouped)


def generate_takeaways_with_llm(
    loves: list[Theme],
    pains: list[Theme],
    *,
    app_name: str | None = None,
    sample_review_count: int,
    on_progress: ProgressFn = None,
) -> list[Takeaway]:
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
        model=takeaway_model(),
    )

    if not data:
        return _fallback_takeaways(loves, pains)

    items = _normalize_llm_takeaways(data, loves=loves, pains=pains)
    if not items:
        return _fallback_takeaways(loves, pains)

    return items
