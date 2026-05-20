import type { QuoteHighlight } from "@/lib/types";

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

export function HighlightedReviewText({
  text,
  highlights = [],
}: {
  text: string;
  highlights?: QuoteHighlight[];
}) {
  const merged = mergeHighlights(highlights);
  if (!merged.length) {
    return <>{text}</>;
  }

  const parts: { bold: boolean; text: string }[] = [];
  let cursor = 0;
  for (const { start, end } of merged) {
    if (start > cursor) {
      parts.push({ bold: false, text: text.slice(cursor, start) });
    }
    parts.push({ bold: true, text: text.slice(start, end) });
    cursor = end;
  }
  if (cursor < text.length) {
    parts.push({ bold: false, text: text.slice(cursor) });
  }

  return (
    <>
      {parts.map((part, index) =>
        part.bold ? (
          <strong key={index} className="font-semibold text-foreground">
            {part.text}
          </strong>
        ) : (
          <span key={index}>{part.text}</span>
        )
      )}
    </>
  );
}

export function matchedPhrases(text: string, highlights: QuoteHighlight[] = []): string[] {
  const merged = mergeHighlights(highlights);
  const phrases = merged.map(({ start, end }) => text.slice(start, end).trim()).filter(Boolean);
  return [...new Set(phrases)];
}
