import type { Quote } from "@/lib/types";

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

export function QuoteCard({ quote }: { quote: Quote }) {
  return (
    <figure className="rounded-xl border border-border/70 bg-white p-5 shadow-sm">
      {quote.rating != null && (
        <div className="mb-2.5">
          <StarRating rating={quote.rating} />
        </div>
      )}
      <blockquote className="text-base leading-relaxed text-foreground sm:text-[17px]">
        {quote.excerpt}
      </blockquote>
      <figcaption className="mt-3 text-sm text-muted-foreground sm:text-base">
        {quote.author}
        <span className="mx-1.5 text-border">·</span>
        {quote.storefront}
        <span className="mx-1.5 text-border">·</span>
        <span className="text-muted-foreground/80">App Store reviewer</span>
      </figcaption>
    </figure>
  );
}
