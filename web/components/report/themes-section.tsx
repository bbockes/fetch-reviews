"use client";

import { AlertTriangle, Heart } from "lucide-react";
import { useState } from "react";

import { ThemeRow } from "@/components/report/theme-row";
import type { Theme } from "@/lib/types";
import { cn } from "@/lib/utils";

export function ThemesSection({
  loves,
  painPoints,
}: {
  loves: Theme[];
  painPoints: Theme[];
}) {
  const [tab, setTab] = useState<"love" | "pain">("love");
  const themes = tab === "love" ? loves : painPoints;
  const maxCount = Math.max(...themes.map((t) => t.mention_count), 1);

  return (
    <section className="rounded-3xl bg-card p-6 shadow-card ring-1 ring-border/50 sm:p-8">
      <h2 className="text-label">What users love vs. what hurts</h2>

      <div className="mt-6 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => setTab("love")}
          className={cn(
            "inline-flex min-h-11 items-center gap-2 rounded-full px-5 py-2.5 text-sm font-medium transition-all duration-200",
            tab === "love"
              ? "bg-foreground text-background shadow-sm"
              : "bg-secondary text-muted-foreground hover:text-foreground"
          )}
        >
          <Heart className="size-4" strokeWidth={1.75} />
          What they love
        </button>
        <button
          type="button"
          onClick={() => setTab("pain")}
          className={cn(
            "inline-flex min-h-11 items-center gap-2 rounded-full px-5 py-2.5 text-sm font-medium transition-all duration-200",
            tab === "pain"
              ? "bg-foreground text-background shadow-sm"
              : "bg-secondary text-muted-foreground hover:text-foreground"
          )}
        >
          <AlertTriangle className="size-4" strokeWidth={1.75} />
          Pain points
        </button>
      </div>

      <div className="mt-2">
        {themes.length === 0 ? (
          <p className="py-12 text-center text-sm text-muted-foreground">
            No themes in this category.
          </p>
        ) : (
          themes.map((theme) => (
            <ThemeRow
              key={theme.title}
              theme={theme}
              variant={tab}
              maxCount={maxCount}
            />
          ))
        )}
      </div>
    </section>
  );
}
