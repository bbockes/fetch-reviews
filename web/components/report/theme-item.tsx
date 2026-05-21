"use client";

import { ChevronDown, ChevronLeft, ChevronRight } from "lucide-react";
import { useEffect, useState } from "react";

import { QuoteCard } from "@/components/report/quote-card";
import type { Theme } from "@/lib/types";
import { cn } from "@/lib/utils";

const QUOTES_PER_PAGE = 1;

/** Fixed viewport — pagination stays put; long quotes scroll inside the card. */
const QUOTE_VIEWPORT_EXCERPT = "h-52";
const QUOTE_VIEWPORT_FULL = "h-[17.6rem]";

const PANEL = {
  panel: "bg-zinc-100",
  chevron: "bg-zinc-600",
  barTrack: "bg-zinc-200/90",
  count: "text-muted-foreground",
  btnOutline: "border-zinc-300/90 bg-white text-foreground hover:bg-zinc-50",
  btnDisabled: "border-zinc-200 bg-white/70 text-zinc-400",
} as const;

export function ThemeItem({
  theme,
  variant,
  maxCount,
  showFullQuote,
  open,
  onToggle,
}: {
  theme: Theme;
  variant: "love" | "pain";
  maxCount: number;
  showFullQuote?: boolean;
  open: boolean;
  onToggle: () => void;
}) {
  const [quotePage, setQuotePage] = useState(0);
  const accent = PANEL;

  const quotes = theme.quotes;
  const quotePageCount = Math.max(1, Math.ceil(quotes.length / QUOTES_PER_PAGE));
  const quoteStart = quotePage * QUOTES_PER_PAGE;
  const visibleQuote = quotes[quoteStart];
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
        onClick={onToggle}
        aria-expanded={open}
        className={cn(
          "flex w-full cursor-pointer items-center gap-3 bg-white py-4 text-left transition-colors",
          !open && "hover:bg-secondary/40"
        )}
      >
        <span className="w-[38%] shrink-0 truncate text-base font-medium text-foreground sm:w-[34%]">
          {theme.title}
        </span>
        <div
          className={cn(
            "hidden h-2 min-w-0 flex-1 overflow-hidden rounded-full sm:block",
            open ? accent.barTrack : "bg-secondary"
          )}
        >
          <div
            className={cn("h-full rounded-full transition-all", barColor)}
            style={{ width: `${barPct}%` }}
          />
        </div>
        <span
          className={cn(
            "w-8 shrink-0 text-right text-base tabular-nums",
            open ? accent.count : "text-muted-foreground"
          )}
        >
          {theme.mention_count}
        </span>
        <span className="relative grid size-7 shrink-0 place-items-center">
          <span
            className={cn(
              "absolute inset-0 rounded-full transition-opacity duration-200",
              open ? cn(accent.chevron, "opacity-100") : "opacity-0"
            )}
            aria-hidden
          />
          <ChevronDown
            className={cn(
              "relative z-[1] size-4 transition-transform duration-200",
              open ? "rotate-180 text-white" : "text-muted-foreground"
            )}
            aria-hidden
          />
        </span>
      </button>

      {open && (
        <div
          className={cn(
            "relative -mx-4 rounded-b-xl px-4 pb-5 pt-1 sm:-mx-6 sm:px-6 sm:pt-2",
            accent.panel
          )}
        >
          <div className="h-2 overflow-hidden rounded-full bg-secondary sm:hidden">
            <div className={cn("h-full rounded-full", barColor)} style={{ width: `${barPct}%` }} />
          </div>

          {quotes.length === 0 ? (
            <p className="text-sm text-muted-foreground sm:text-base">No reviews for this theme.</p>
          ) : (
            <>
              <p className="mt-4 text-sm text-muted-foreground sm:text-base">
                Showing {quoteStart + 1} of {theme.mention_count}
                {quotes.length < theme.mention_count && (
                  <span className="opacity-80"> ({quotes.length} reviews available)</span>
                )}
              </p>

              <div
                className={cn(
                  "mt-4",
                  showFullQuote ? QUOTE_VIEWPORT_FULL : QUOTE_VIEWPORT_EXCERPT
                )}
              >
                {visibleQuote && (
                  <QuoteCard
                    key={`${visibleQuote.author}-${quoteStart}-${showFullQuote ? "full" : "excerpt"}`}
                    quote={visibleQuote}
                    showFullQuote={showFullQuote}
                    className="h-full min-h-0"
                  />
                )}
              </div>

              <div
                className={cn(
                  "mt-4 flex items-center justify-center gap-3",
                  quotePageCount <= 1 && "invisible"
                )}
                aria-hidden={quotePageCount <= 1}
              >
                <button
                  type="button"
                  onClick={() => setQuotePage((p) => p - 1)}
                  disabled={!canPrev}
                  aria-label="Previous review"
                  tabIndex={quotePageCount <= 1 ? -1 : 0}
                  className={cn(
                    "inline-flex size-9 items-center justify-center rounded-lg border transition-colors",
                    canPrev ? accent.btnOutline : accent.btnDisabled
                  )}
                >
                  <ChevronLeft className="size-4" />
                </button>
                <span
                  className={cn(
                    "min-w-[4.5rem] text-center text-sm tabular-nums sm:text-base",
                    accent.count
                  )}
                >
                  {quotePage + 1} / {quotePageCount}
                </span>
                <button
                  type="button"
                  onClick={() => setQuotePage((p) => p + 1)}
                  disabled={!canNext}
                  aria-label="Next review"
                  tabIndex={quotePageCount <= 1 ? -1 : 0}
                  className={cn(
                    "inline-flex size-9 items-center justify-center rounded-lg border transition-colors",
                    canNext ? accent.btnOutline : accent.btnDisabled
                  )}
                >
                  <ChevronRight className="size-4" />
                </button>
              </div>
            </>
          )}

          {theme.also_noted && quotes.length < theme.mention_count && (
            <p className="mt-4 text-sm text-muted-foreground sm:text-base">{theme.also_noted}</p>
          )}
        </div>
      )}
    </li>
  );
}
