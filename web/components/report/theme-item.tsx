"use client";

import { ChevronDown, ChevronLeft, ChevronRight } from "lucide-react";
import { useEffect, useState } from "react";

import { QuoteCard } from "@/components/report/quote-card";
import type { Theme } from "@/lib/types";
import { cn } from "@/lib/utils";

const PREVIEW_LEN = 120;
const QUOTES_PER_PAGE = 5;

export function ThemeItem({ theme, rank }: { theme: Theme; rank: number }) {
  const [open, setOpen] = useState(false);
  const [quotePage, setQuotePage] = useState(0);

  const quotes = theme.quotes;
  const quotePageCount = Math.max(1, Math.ceil(quotes.length / QUOTES_PER_PAGE));
  const quoteStart = quotePage * QUOTES_PER_PAGE;
  const visibleQuotes = quotes.slice(quoteStart, quoteStart + QUOTES_PER_PAGE);
  const canPrevQuotes = quotePage > 0;
  const canNextQuotes = quotePage < quotePageCount - 1;

  useEffect(() => {
    if (!open) setQuotePage(0);
  }, [open]);

  useEffect(() => {
    if (quotePage > quotePageCount - 1) setQuotePage(Math.max(0, quotePageCount - 1));
  }, [quotePage, quotePageCount]);

  const preview = quotes[0]?.excerpt;
  const truncated =
    preview && preview.length > PREVIEW_LEN
      ? preview.slice(0, PREVIEW_LEN).trim() + "…"
      : preview;

  return (
    <li className="py-6">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="group flex w-full gap-4 text-left"
      >
        <span className="w-8 shrink-0 pt-0.5 text-[14px] tabular-nums text-subtle">
          {String(rank).padStart(2, "0")}
        </span>
        <span className="min-w-0 flex-1">
          <span className="flex items-start justify-between gap-4">
            <span className="text-[21px] font-semibold tracking-[-0.02em] text-foreground">
              {theme.title}
            </span>
            <span className="shrink-0 pt-1 text-[14px] tabular-nums text-subtle">
              {theme.mention_count} mentions
            </span>
          </span>
          {!open && truncated && (
            <p className="mt-2 line-clamp-2 text-[17px] leading-relaxed text-subtle">
              &ldquo;{truncated}&rdquo;
            </p>
          )}
        </span>
        <ChevronDown
          className={cn(
            "mt-1 size-5 shrink-0 text-subtle transition-transform duration-300",
            open && "rotate-180"
          )}
          strokeWidth={1.5}
          aria-hidden
        />
      </button>

      {open && (
        <div className="mt-6 space-y-4 pl-12">
          {quotes.length === 0 ? (
            <p className="text-[17px] text-subtle">No quote excerpts available for this theme.</p>
          ) : (
            <>
              {quotePageCount > 1 && (
                <p className="text-[12px] tabular-nums text-subtle">
                  Showing {quoteStart + 1}–{Math.min(quoteStart + QUOTES_PER_PAGE, quotes.length)}{" "}
                  of {theme.mention_count} mentions
                  {quotes.length < theme.mention_count && (
                    <span className="text-subtle/80">
                      {" "}
                      ({quotes.length} excerpts available)
                    </span>
                  )}
                </p>
              )}

              {visibleQuotes.map((quote, i) => (
                <QuoteCard key={`${quote.author}-${quoteStart + i}`} quote={quote} />
              ))}

              {quotePageCount > 1 && (
                <div className="flex items-center justify-center gap-4 pt-2">
                  <button
                    type="button"
                    onClick={() => setQuotePage((p) => p - 1)}
                    disabled={!canPrevQuotes}
                    aria-label="Previous mentions"
                    className={cn(
                      "inline-flex size-10 items-center justify-center rounded-full border border-border bg-white transition-colors",
                      canPrevQuotes
                        ? "text-foreground hover:bg-secondary"
                        : "cursor-not-allowed text-subtle/40"
                    )}
                  >
                    <ChevronLeft className="size-5" strokeWidth={1.5} />
                  </button>
                  <span className="min-w-[5rem] text-center text-[12px] tabular-nums text-subtle">
                    Page {quotePage + 1} of {quotePageCount}
                  </span>
                  <button
                    type="button"
                    onClick={() => setQuotePage((p) => p + 1)}
                    disabled={!canNextQuotes}
                    aria-label="Next mentions"
                    className={cn(
                      "inline-flex size-10 items-center justify-center rounded-full border border-border bg-white transition-colors",
                      canNextQuotes
                        ? "text-foreground hover:bg-secondary"
                        : "cursor-not-allowed text-subtle/40"
                    )}
                  >
                    <ChevronRight className="size-5" strokeWidth={1.5} />
                  </button>
                </div>
              )}
            </>
          )}

          {theme.also_noted && quotes.length < theme.mention_count && (
            <p className="text-[14px] text-subtle">{theme.also_noted}</p>
          )}
        </div>
      )}
    </li>
  );
}
