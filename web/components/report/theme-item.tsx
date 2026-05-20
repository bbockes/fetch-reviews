"use client";

import { ChevronLeft, ChevronRight, ChevronRight as ChevronExpand } from "lucide-react";
import { useEffect, useState } from "react";

import { QuoteCard } from "@/components/report/quote-card";
import type { Theme } from "@/lib/types";
import { cn } from "@/lib/utils";

const QUOTES_PER_PAGE = 3;

export function ThemeItem({
  theme,
  variant,
  maxCount,
}: {
  theme: Theme;
  variant: "love" | "pain";
  maxCount: number;
}) {
  const [open, setOpen] = useState(false);
  const [quotePage, setQuotePage] = useState(0);

  const quotes = theme.quotes;
  const quotePageCount = Math.max(1, Math.ceil(quotes.length / QUOTES_PER_PAGE));
  const quoteStart = quotePage * QUOTES_PER_PAGE;
  const visibleQuotes = quotes.slice(quoteStart, quoteStart + QUOTES_PER_PAGE);
  const barPct = maxCount ? (theme.mention_count / maxCount) * 100 : 0;
  const barColor = variant === "love" ? "bg-emerald-500" : "bg-red-500";

  useEffect(() => {
    if (!open) setQuotePage(0);
  }, [open]);

  useEffect(() => {
    if (quotePage > quotePageCount - 1) setQuotePage(Math.max(0, quotePageCount - 1));
  }, [quotePage, quotePageCount]);

  const canPrev = quotePage > 0;
  const canNext = quotePage < quotePageCount - 1;

  return (
    <li className="border-b border-border/60 last:border-b-0">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex w-full cursor-pointer items-center gap-3 py-4 text-left transition-colors hover:bg-secondary/40"
      >
        <span className="w-[38%] shrink-0 truncate text-base font-medium text-foreground sm:w-[34%]">
          {theme.title}
        </span>
        <div className="hidden h-2 min-w-0 flex-1 overflow-hidden rounded-full bg-secondary sm:block">
          <div
            className={cn("h-full rounded-full transition-all", barColor)}
            style={{ width: `${barPct}%` }}
          />
        </div>
        <span className="w-8 shrink-0 text-right text-base tabular-nums text-muted-foreground">
          {theme.mention_count}
        </span>
        <ChevronExpand
          className={cn(
            "size-4 shrink-0 text-muted-foreground transition-transform duration-200",
            open && "rotate-90"
          )}
          aria-hidden
        />
      </button>

      {open && (
        <div className="space-y-4 border-t border-border/50 bg-white px-2 py-4 sm:px-3">
          <div className="h-2 overflow-hidden rounded-full bg-secondary sm:hidden">
            <div className={cn("h-full rounded-full", barColor)} style={{ width: `${barPct}%` }} />
          </div>

          {quotes.length === 0 ? (
            <p className="text-sm text-muted-foreground sm:text-base">No quote excerpts for this theme.</p>
          ) : (
            <>
              <p className="text-sm text-muted-foreground sm:text-base">
                Showing {quoteStart + 1}–{Math.min(quoteStart + QUOTES_PER_PAGE, quotes.length)} of{" "}
                {theme.mention_count}
                {quotes.length < theme.mention_count && (
                  <span> ({quotes.length} excerpts available)</span>
                )}
              </p>

              <div className="space-y-4">
                {visibleQuotes.map((quote, i) => (
                  <QuoteCard key={`${quote.author}-${quoteStart + i}`} quote={quote} />
                ))}
              </div>

              {quotePageCount > 1 && (
                <div className="flex items-center justify-center gap-3 pt-1">
                  <button
                    type="button"
                    onClick={() => setQuotePage((p) => p - 1)}
                    disabled={!canPrev}
                    aria-label="Previous quotes"
                    className={cn(
                      "inline-flex size-9 items-center justify-center rounded-lg border border-border bg-white transition-colors",
                      canPrev
                        ? "text-foreground hover:bg-secondary"
                        : "cursor-not-allowed text-muted-foreground/40"
                    )}
                  >
                    <ChevronLeft className="size-4" />
                  </button>
                  <span className="min-w-[4.5rem] text-center text-sm tabular-nums text-muted-foreground sm:text-base">
                    {quotePage + 1} / {quotePageCount}
                  </span>
                  <button
                    type="button"
                    onClick={() => setQuotePage((p) => p + 1)}
                    disabled={!canNext}
                    aria-label="Next quotes"
                    className={cn(
                      "inline-flex size-9 items-center justify-center rounded-lg border border-border bg-white transition-colors",
                      canNext
                        ? "text-foreground hover:bg-secondary"
                        : "cursor-not-allowed text-muted-foreground/40"
                    )}
                  >
                    <ChevronRight className="size-4" />
                  </button>
                </div>
              )}
            </>
          )}

          {theme.also_noted && quotes.length < theme.mention_count && (
            <p className="text-sm text-muted-foreground sm:text-base">{theme.also_noted}</p>
          )}
        </div>
      )}
    </li>
  );
}
