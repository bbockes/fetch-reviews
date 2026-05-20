"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { useEffect, useState } from "react";

import { QuoteCard } from "@/components/report/quote-card";
import type { Quote } from "@/lib/types";
import { cn } from "@/lib/utils";

const PER_PAGE = 3;

export function QuotesPager({
  quotes,
  mentionCount,
  variant,
}: {
  quotes: Quote[];
  mentionCount: number;
  variant: "love" | "pain";
}) {
  const [page, setPage] = useState(0);
  const total = quotes.length;
  const pageCount = Math.max(1, Math.ceil(total / PER_PAGE));

  useEffect(() => {
    setPage(0);
  }, [quotes, mentionCount]);

  useEffect(() => {
    if (page > pageCount - 1) setPage(Math.max(0, pageCount - 1));
  }, [page, pageCount]);

  if (total === 0) {
    return (
      <p className="text-sm text-muted-foreground">No quote excerpts available for this theme.</p>
    );
  }

  const start = page * PER_PAGE;
  const end = Math.min(start + PER_PAGE, total);
  const visible = quotes.slice(start, end);
  const canPrev = page > 0;
  const canNext = page < pageCount - 1;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-2 text-xs text-muted-foreground">
        <span>
          Showing {start + 1}–{end} of {mentionCount}
          {total < mentionCount && (
            <span className="text-muted-foreground/80">
              {" "}
              ({total} excerpts available)
            </span>
          )}
        </span>
        {pageCount > 1 && (
          <span className="tabular-nums">
            Page {page + 1} of {pageCount}
          </span>
        )}
      </div>

      {visible.map((quote, i) => (
        <QuoteCard key={`${quote.author}-${start + i}`} quote={quote} variant={variant} />
      ))}

      {pageCount > 1 && (
        <div className="flex items-center justify-center gap-3 pt-2">
          <button
            type="button"
            onClick={() => setPage((p) => p - 1)}
            disabled={!canPrev}
            aria-label="Previous quotes"
            className={cn(
              "inline-flex size-10 items-center justify-center rounded-full bg-secondary transition-all duration-200",
              canPrev
                ? "text-foreground hover:bg-[#e0e0e0]"
                : "cursor-not-allowed text-muted-foreground/40"
            )}
          >
            <ChevronLeft className="size-4" strokeWidth={1.75} />
          </button>
          <button
            type="button"
            onClick={() => setPage((p) => p + 1)}
            disabled={!canNext}
            aria-label="Next quotes"
            className={cn(
              "inline-flex size-10 items-center justify-center rounded-full bg-secondary transition-all duration-200",
              canNext
                ? "text-foreground hover:bg-[#e0e0e0]"
                : "cursor-not-allowed text-muted-foreground/40"
            )}
          >
            <ChevronRight className="size-4" strokeWidth={1.75} />
          </button>
        </div>
      )}
    </div>
  );
}
