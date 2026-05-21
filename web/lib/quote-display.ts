import type { Quote, QuoteHighlight } from "@/lib/types";

const ELLIPSIS = "…";
const PASSAGE_JOINER = " … ";

function normalizeQuotes(s: string): string {
  return s.replace(/\u2018|\u2019/g, "'").replace(/\u201C|\u201D/g, '"');
}

function mergeHighlights(highlights: QuoteHighlight[]): QuoteHighlight[] {
  if (!highlights.length) return [];
  const sorted = [...highlights].sort((a, b) => a.start - b.start);
  const merged: QuoteHighlight[] = [{ ...sorted[0] }];
  for (const span of sorted.slice(1)) {
    const prev = merged[merged.length - 1];
    if (span.start <= prev.end) {
      prev.end = Math.max(prev.end, span.end);
    } else {
      merged.push({ ...span });
    }
  }
  return merged;
}

function flexibleWhitespaceIndex(full: string, passage: string): number {
  const trimmed = passage.trim();
  if (!trimmed) return -1;
  const escaped = trimmed.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const pattern = new RegExp(escaped.replace(/\s+/g, "\\s+"), "u");
  const match = pattern.exec(full);
  return match?.index ?? -1;
}

/** Locate theme passage inside the full review (handles whitespace / quote variants). */
export function locatePassageInFull(full: string, passage: string): number {
  if (!passage || !full) return -1;
  if (full.includes(passage)) return full.indexOf(passage);

  const normalizedIdx = normalizeQuotes(full).indexOf(normalizeQuotes(passage));
  if (normalizedIdx >= 0) return normalizedIdx;

  const flex = flexibleWhitespaceIndex(full, passage);
  if (flex >= 0) return flex;

  const flexNorm = flexibleWhitespaceIndex(normalizeQuotes(full), normalizeQuotes(passage));
  if (flexNorm >= 0) return flexNorm;

  const parts = passage
    .split(PASSAGE_JOINER)
    .map((p) => p.trim())
    .filter(Boolean);
  if (parts.length > 1) {
    const first = parts[0];
    return locatePassageInFull(full, first);
  }

  return -1;
}

/** Theme passage shown in excerpt / bolded in full review (full display_text, not a phrase slice). */
export function themePassage(quote: Quote): string | null {
  const raw = stripEdgeEllipsis(quote.text?.trim() || "");
  return raw || null;
}

function findHighlightsByPhrase(full: string, phrase: string): QuoteHighlight[] {
  const trimmed = phrase.trim();
  if (!trimmed) return [];
  const idx = locatePassageInFull(full, trimmed);
  if (idx < 0) return [];

  const flex = new RegExp(
    trimmed
      .replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
      .replace(/['\u2018\u2019]/g, "['\u2018\u2019]")
      .replace(/["\u201C\u201D]/g, '["\u201C\u201D]')
      .replace(/\s+/g, "\\s+"),
    "u"
  );
  const match = flex.exec(full.slice(idx));
  const len = match?.[0].length ?? trimmed.length;
  return [{ start: idx, end: idx + len }];
}

export function fullReviewDisplay(quote: Quote): {
  text: string;
  highlights: QuoteHighlight[];
} | null {
  const passage = themePassage(quote);
  if (!passage) return null;

  const full = quote.full_text?.trim() || "";
  if (!full) {
    return { text: passage, highlights: [{ start: 0, end: passage.length }] };
  }

  const idx = locatePassageInFull(full, passage);
  if (idx >= 0) {
    const flex = new RegExp(
      passage
        .replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
        .replace(/['\u2018\u2019]/g, "['\u2018\u2019]")
        .replace(/["\u201C\u201D]/g, '["\u201C\u201D]')
        .replace(/\s+/g, "\\s+"),
      "u"
    );
    const match = flex.exec(full.slice(idx));
    const len = match?.[0].length ?? passage.length;
    return {
      text: full,
      highlights: [{ start: idx, end: idx + len }],
    };
  }

  const fallback = findHighlightsByPhrase(full, passage);
  return { text: full, highlights: fallback };
}

/** Plain text to copy — excerpt passage or full review, per toggle. */
export function quoteCopyText(quote: Quote, showFullQuote: boolean): string {
  if (showFullQuote) {
    const display = fullReviewDisplay(quote);
    return display?.text ?? themePassage(quote) ?? "";
  }
  return passageDisplay(quote)?.text ?? themePassage(quote) ?? "";
}

/** Excerpt mode: full theme passage, fully bold. */
export function passageDisplay(quote: Quote): {
  text: string;
  highlights: QuoteHighlight[];
} | null {
  const passage = themePassage(quote);
  if (!passage) return null;

  return {
    text: passage,
    highlights: [{ start: 0, end: passage.length }],
  };
}

export function stripEdgeEllipsis(text: string): string {
  let s = text.trim();
  while (s.startsWith(ELLIPSIS) || s.startsWith("...")) {
    s = (s.startsWith(ELLIPSIS) ? s.slice(ELLIPSIS.length) : s.slice(3)).trimStart();
  }
  while (s.endsWith(ELLIPSIS) || s.endsWith("...")) {
    s = (s.endsWith(ELLIPSIS) ? s.slice(0, -ELLIPSIS.length) : s.slice(0, -3)).trimEnd();
  }
  return s;
}
