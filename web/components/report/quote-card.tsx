import type { Quote } from "@/lib/types";

function stars(rating: number | null) {
  if (rating == null) return null;
  return (
    <span className="text-[12px] tracking-wider text-subtle" aria-label={`${rating} out of 5 stars`}>
      {"★".repeat(rating)}
      <span className="text-border">{"☆".repeat(5 - rating)}</span>
    </span>
  );
}

export function QuoteCard({ quote }: { quote: Quote }) {
  return (
    <figure className="border-l-2 border-foreground/15 pl-5">
      <blockquote className="text-[17px] leading-relaxed text-foreground">
        &ldquo;{quote.excerpt}&rdquo;
      </blockquote>
      <figcaption className="mt-3 flex flex-wrap items-center gap-x-2 text-[12px] text-subtle">
        <span>{quote.author}</span>
        <span aria-hidden>·</span>
        <span>{quote.storefront}</span>
        {quote.rating != null && (
          <>
            <span aria-hidden>·</span>
            {stars(quote.rating)}
          </>
        )}
      </figcaption>
    </figure>
  );
}
