import { HighlightedReviewText } from "@/components/report/highlighted-review-text";
import type { Quote } from "@/lib/types";
import { fullReviewDisplay, passageDisplay } from "@/lib/quote-display";
import { cn } from "@/lib/utils";

function QuoteFullText({ quote }: { quote: Quote }) {
  const display = fullReviewDisplay(quote);
  if (!display) return null;

  return <HighlightedReviewText text={display.text} highlights={display.highlights} />;
}

function QuoteExcerpt({ quote }: { quote: Quote }) {
  const display = passageDisplay(quote);
  if (!display) return null;

  return (
    <HighlightedReviewText text={display.text} highlights={display.highlights} />
  );
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

export function QuoteCard({
  quote,
  showFullQuote = false,
  className,
}: {
  quote: Quote;
  showFullQuote?: boolean;
  className?: string;
}) {
  return (
    <figure
      className={cn(
        "flex flex-col rounded-xl border border-border/70 bg-white p-5 shadow-sm",
        className
      )}
    >
      {quote.rating != null && (
        <div className="mb-2.5">
          <StarRating rating={quote.rating} />
        </div>
      )}
      <blockquote className="max-h-[16rem] flex-1 overflow-y-auto whitespace-pre-wrap text-base leading-relaxed text-foreground sm:text-[17px]">
        {showFullQuote ? <QuoteFullText quote={quote} /> : <QuoteExcerpt quote={quote} />}
      </blockquote>
      <figcaption className="mt-3 text-sm text-muted-foreground sm:text-base">
        {quote.author}
        <span className="mx-1.5 text-border">·</span>
        {quote.storefront}
      </figcaption>
    </figure>
  );
}
