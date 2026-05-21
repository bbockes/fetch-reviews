"""Trim theme quotes to relevant passages and bold full sentiment sentences."""

from __future__ import annotations

import json
import re

from .llm import complete_json, llm_configured
from .models import Quote, QuoteHighlight

_BATCH_SIZE = 6


def refine_quotes_for_theme(quotes: list[Quote], theme_title: str) -> list[Quote]:
    """Return quotes with trimmed text and sentence-level highlights."""
    if not quotes:
        return quotes

    if llm_configured():
        try:
            return _refine_with_llm(quotes, theme_title)
        except Exception:
            pass

    return [_heuristic_refine_quote(quote) for quote in quotes]


def _split_sentences(text: str) -> list[tuple[int, int, str]]:
    sentences: list[tuple[int, int, str]] = []
    for match in re.finditer(r"[^\n.!?]+(?:[.!?]+(?=\s|$|\n)|\n+)|[^\n]+", text):
        start, end = match.start(), match.end()
        chunk = text[start:end]
        if chunk.strip():
            sentences.append((start, end, chunk))
    if not sentences and text.strip():
        sentences.append((0, len(text), text))
    return sentences


def _highlight_spans_for_substrings(text: str, substrings: list[str]) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    cursor = 0
    for substring in substrings:
        needle = substring.strip()
        if not needle:
            continue
        idx = text.find(needle, cursor)
        if idx < 0:
            idx = text.find(needle)
        if idx >= 0:
            spans.append((idx, idx + len(needle)))
            cursor = idx + len(needle)
    return _merge_spans(spans)


def _merge_spans(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not spans:
        return []
    spans = sorted(spans)
    merged = [spans[0]]
    for start, end in spans[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def _heuristic_refine_quote(quote: Quote) -> Quote:
    """Fallback: keep theme-matching sentences and bold each whole sentence."""
    body = quote.text.strip()
    if not body:
        return quote

    sentences = _split_sentences(body)
    if not sentences:
        return quote

    if quote.highlights:
        bold_sentences: list[tuple[int, int, str]] = []
        for start, end, chunk in sentences:
            for hl in quote.highlights:
                if start <= hl.start < end or start <= hl.end <= end or (
                    hl.start <= start and hl.end >= end
                ):
                    bold_sentences.append((start, end, chunk))
                    break
    else:
        bold_sentences = sentences[:1]

    if not bold_sentences:
        bold_sentences = sentences[:1]

    ordered = sorted({(s, e, c) for s, e, c in bold_sentences}, key=lambda item: item[0])
    ordered = ordered[:3]

    display_text = " ".join(chunk.strip() for _, _, chunk in ordered)
    bold_chunks = [chunk.strip() for _, _, chunk in ordered]
    highlight_spans = _highlight_spans_for_substrings(display_text, bold_chunks)

    return quote.model_copy(
        update={
            "text": display_text,
            "highlights": [
                QuoteHighlight(start=start, end=end) for start, end in highlight_spans
            ],
            "excerpt": _excerpt(display_text),
        }
    )


def _excerpt(text: str, max_len: int = 180) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rsplit(" ", 1)[0] + "…"


def _refine_with_llm(quotes: list[Quote], theme_title: str) -> list[Quote]:
    refined = list(quotes)

    schema = {
        "type": "object",
        "properties": {
            "quotes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "index": {"type": "integer"},
                        "display_text": {"type": "string"},
                        "bold_text": {"type": "string"},
                    },
                    "required": ["index", "display_text", "bold_text"],
                },
            }
        },
        "required": ["quotes"],
    }

    for batch_start in range(0, len(quotes), _BATCH_SIZE):
        batch = quotes[batch_start : batch_start + _BATCH_SIZE]
        payload = [
            {
                "index": batch_start + i,
                "author": quote.author,
                "rating": quote.rating,
                "review": quote.text,
            }
            for i, quote in enumerate(batch)
        ]

        data = complete_json(
            system=(
                "You trim App Store reviews for a theme report. "
                "For each review, produce a short verbatim excerpt focused on the theme — "
                "usually 1–3 sentences. Omit unrelated content (pricing elsewhere, "
                "off-topic praise, setup stories, etc.). "
                "Use exact wording from the review; do not paraphrase. "
                "If you skip middle content, join excerpts with ' … '. "
                "bold_text must be an exact substring of display_text: the full sentence "
                "(or full consecutive sentences) that express the theme sentiment. "
                "Bold entire sentences, not individual phrases."
            ),
            user=json.dumps({"theme": theme_title, "reviews": payload}, ensure_ascii=False),
            tool_name="refined_quotes",
            schema=schema,
        )
        if not data:
            continue

        for item in data.get("quotes", []):
            idx = item.get("index")
            if not isinstance(idx, int) or idx < 0 or idx >= len(refined):
                continue

            display_text = (item.get("display_text") or "").strip()
            bold_text = (item.get("bold_text") or "").strip()
            if not display_text:
                continue

            original = refined[idx]
            if bold_text and bold_text not in display_text:
                bold_text = _best_bold_fallback(display_text, bold_text, original.text)

            highlight_spans = (
                _highlight_spans_for_substrings(display_text, [bold_text])
                if bold_text
                else []
            )
            if not highlight_spans:
                highlight_spans = _sentence_spans_for_phrase(display_text, bold_text)

            refined[idx] = original.model_copy(
                update={
                    "text": display_text,
                    "highlights": [
                        QuoteHighlight(start=start, end=end)
                        for start, end in highlight_spans
                    ],
                    "excerpt": _excerpt(display_text),
                }
            )

    return refined


def _best_bold_fallback(display_text: str, bold_text: str, original: str) -> str:
    """Pick a full sentence from display_text when the model's bold_text doesn't match."""
    for sentence in _split_sentences(display_text):
        _, _, chunk = sentence
        stripped = chunk.strip()
        if bold_text.lower() in stripped.lower():
            return stripped
    for sentence in _split_sentences(original):
        _, _, chunk = sentence
        stripped = chunk.strip()
        if bold_text.lower() in stripped.lower() and stripped in display_text:
            return stripped
    sentences = [chunk.strip() for _, _, chunk in _split_sentences(display_text)]
    return sentences[0] if sentences else bold_text


def _sentence_spans_for_phrase(text: str, phrase: str) -> list[tuple[int, int]]:
    if not phrase:
        return []
    lowered = text.lower()
    idx = lowered.find(phrase.lower())
    if idx < 0:
        return []
    for start, end, _ in _split_sentences(text):
        if start <= idx < end:
            return [(start, end)]
    return []
