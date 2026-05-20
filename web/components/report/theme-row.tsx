"use client";

import { ChevronRight } from "lucide-react";
import { useState } from "react";

import { QuotesPager } from "@/components/report/quotes-pager";
import type { Theme } from "@/lib/types";
import { cn } from "@/lib/utils";

export function ThemeRow({
  theme,
  variant,
  maxCount,
}: {
  theme: Theme;
  variant: "love" | "pain";
  maxCount: number;
}) {
  const [open, setOpen] = useState(false);
  const barPct = maxCount ? (theme.mention_count / maxCount) * 100 : 0;
  const barColor = variant === "love" ? "bg-foreground" : "bg-brand";

  return (
    <div className="border-b border-border/60 last:border-b-0">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex w-full min-h-12 cursor-pointer items-center gap-4 rounded-xl px-2 py-4 text-left transition-colors hover:bg-surface-muted/80"
      >
        <span className="w-[42%] shrink-0 truncate text-sm font-medium text-foreground sm:w-[38%]">
          {theme.title}
        </span>
        <div className="hidden h-2 min-w-0 flex-1 overflow-hidden rounded-full bg-muted sm:block">
          <div
            className={cn("h-full rounded-full transition-all duration-300", barColor)}
            style={{ width: `${barPct}%` }}
          />
        </div>
        <span className="w-8 shrink-0 text-right text-sm tabular-nums text-muted-foreground">
          {theme.mention_count}
        </span>
        <ChevronRight
          className={cn(
            "size-4 shrink-0 text-muted-foreground transition-transform duration-200",
            open && "rotate-90"
          )}
          aria-hidden
        />
      </button>

      {open && (
        <div className="space-y-4 rounded-2xl bg-surface-muted/60 px-3 py-5 sm:px-4">
          <div className="h-2 overflow-hidden rounded-full bg-muted sm:hidden">
            <div
              className={cn("h-full rounded-full", barColor)}
              style={{ width: `${barPct}%` }}
            />
          </div>
          <QuotesPager
            quotes={theme.quotes}
            mentionCount={theme.mention_count}
            variant={variant}
          />
          {theme.also_noted && theme.quotes.length < theme.mention_count && (
            <p className="text-xs text-muted-foreground">{theme.also_noted}</p>
          )}
        </div>
      )}
    </div>
  );
}
