import type { Quote } from "@/lib/types";
import { cn } from "@/lib/utils";

function stars(rating: number | null) {
  if (rating == null) return null;
  return (
    <span className="text-foreground/70">
      {"★".repeat(rating)}
      <span className="text-muted-foreground/30">{"☆".repeat(5 - rating)}</span>
    </span>
  );
}

export function QuoteCard({
  quote,
  variant,
}: {
  quote: Quote;
  variant: "love" | "pain";
}) {
  return (
    <blockquote
      className={cn(
        "rounded-2xl bg-white px-5 py-4 shadow-card ring-1 ring-border/40",
        variant === "love"
          ? "border-l-[3px] border-l-foreground"
          : "border-l-[3px] border-l-brand"
      )}
    >
      <div className="mb-3 flex items-center justify-between gap-2 text-xs text-muted-foreground">
        <span className="font-medium">
          {quote.author}
          <span className="mx-1.5 font-normal text-border">·</span>
          {quote.storefront}
        </span>
        {stars(quote.rating)}
      </div>
      <p className="text-sm leading-relaxed text-foreground/90">
        &ldquo;{quote.excerpt}&rdquo;
      </p>
    </blockquote>
  );
}
