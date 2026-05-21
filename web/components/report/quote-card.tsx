"use client";

import { Check, Copy } from "lucide-react";
import { useCallback, useMemo, useState } from "react";

import { HighlightedReviewText } from "@/components/report/highlighted-review-text";
import type { Quote } from "@/lib/types";
import {
  fullReviewDisplay,
  passageDisplay,
  quoteCopyText,
} from "@/lib/quote-display";
import { cn } from "@/lib/utils";

/** ~52rem — a bit wider than 720px, still comfortable for long review text */
const QUOTE_TEXT_MAX_WIDTH = "max-w-[52rem]";

function QuoteFullText({ quote }: { quote: Quote }) {
  const display = fullReviewDisplay(quote);
  if (!display) return null;

  return <HighlightedReviewText text={display.text} highlights={display.highlights} />;
}

function QuoteExcerpt({ quote }: { quote: Quote }) {
  const display = passageDisplay(quote);
  if (!display) return null;

  return <strong className="font-semibold text-foreground">{display.text}</strong>;
}

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex gap-0.5" aria-label={`${rating} out of 5 stars`}>
      {Array.from({ length: 5 }, (_, i) => (
        <span
          key={i}
          className={`text-lg leading-none ${i < rating ? "text-amber-400" : "text-border"}`}
        >
          ★
        </span>
      ))}
    </div>
  );
}

function CopyReviewButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const copy = useCallback(async () => {
    if (!text.trim()) return;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  }, [text]);

  return (
    <button
      type="button"
      onClick={copy}
      disabled={!text.trim()}
      aria-label={copied ? "Copied" : "Copy review text"}
      className={cn(
        "inline-flex size-8 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground",
        !text.trim() && "cursor-not-allowed opacity-40"
      )}
    >
      {copied ? <Check className="size-4" aria-hidden /> : <Copy className="size-4" aria-hidden />}
    </button>
  );
}

export function QuoteCard({
  quote,
  showFullQuote = false,
  className,
}: {
  quote: Quote;
  showFullQuote?: boolean;
  className?: string;
}) {
  const textToCopy = useMemo(
    () => quoteCopyText(quote, showFullQuote),
    [quote, showFullQuote]
  );

  return (
    <figure
      className={cn(
        "relative flex min-h-0 flex-col overflow-hidden rounded-xl border border-border/70 bg-white py-5 pl-8 shadow-sm sm:py-6 sm:pl-10",
        className
      )}
    >
      <div className="min-h-0 flex-1 overflow-y-auto pr-2 [scrollbar-gutter:stable] sm:pr-3">
        <div className={cn("mr-auto w-full pb-1 pr-10", QUOTE_TEXT_MAX_WIDTH)}>
          {quote.rating != null && (
            <div className="mb-2.5">
              <StarRating rating={quote.rating} />
            </div>
          )}
          <blockquote className="whitespace-pre-wrap text-base leading-relaxed text-foreground sm:text-[17px]">
            {showFullQuote ? <QuoteFullText quote={quote} /> : <QuoteExcerpt quote={quote} />}
          </blockquote>
          <figcaption className="mt-3 text-sm text-muted-foreground sm:text-base">
            {quote.author}
            <span className="mx-1.5 text-border">·</span>
            {quote.storefront}
          </figcaption>
        </div>
      </div>
      <div className="absolute bottom-4 right-3 sm:bottom-5 sm:right-4">
        <CopyReviewButton text={textToCopy} />
      </div>
    </figure>
  );
}
