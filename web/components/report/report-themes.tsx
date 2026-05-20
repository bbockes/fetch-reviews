"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { useEffect, useState } from "react";

import { ThemeItem } from "@/components/report/theme-item";
import type { Theme } from "@/lib/types";
import { cn } from "@/lib/utils";

const PER_PAGE = 5;

export function ReportThemes({
  loves,
  painPoints,
}: {
  loves: Theme[];
  painPoints: Theme[];
}) {
  const [mode, setMode] = useState<"love" | "pain">("love");
  const [page, setPage] = useState(0);
  const themes = mode === "love" ? loves : painPoints;
  const pageCount = Math.max(1, Math.ceil(themes.length / PER_PAGE));

  useEffect(() => {
    setPage(0);
  }, [mode]);

  useEffect(() => {
    if (page > pageCount - 1) setPage(Math.max(0, pageCount - 1));
  }, [page, pageCount]);

  const start = page * PER_PAGE;
  const visible = themes.slice(start, start + PER_PAGE);
  const canPrev = page > 0;
  const canNext = page < pageCount - 1;

  return (
    <div>
      <div className="flex justify-center">
        <div
          className="inline-flex rounded-full bg-border/40 p-1"
          role="tablist"
          aria-label="Theme category"
        >
          <TabButton active={mode === "love"} onClick={() => setMode("love")}>
            What they love
          </TabButton>
          <TabButton active={mode === "pain"} onClick={() => setMode("pain")}>
            Pain points
          </TabButton>
        </div>
      </div>

      <div className="mt-10" role="tabpanel">
        {themes.length === 0 ? (
          <p className="py-16 text-center text-[17px] text-subtle">
            No themes in this category.
          </p>
        ) : (
          <>
            {pageCount > 1 && (
              <p className="mb-6 text-center text-[12px] tabular-nums text-subtle">
                Showing {start + 1}–{Math.min(start + PER_PAGE, themes.length)} of{" "}
                {themes.length} themes
              </p>
            )}

            <ol className="divide-y divide-border">
              {visible.map((theme, index) => (
                <ThemeItem
                  key={theme.title}
                  theme={theme}
                  rank={start + index + 1}
                />
              ))}
            </ol>

            {pageCount > 1 && (
              <div className="mt-8 flex items-center justify-center gap-4">
                <button
                  type="button"
                  onClick={() => setPage((p) => p - 1)}
                  disabled={!canPrev}
                  aria-label="Previous themes"
                  className={cn(
                    "inline-flex size-10 items-center justify-center rounded-full border border-border bg-white transition-colors",
                    canPrev
                      ? "text-foreground hover:bg-secondary"
                      : "cursor-not-allowed text-subtle/40"
                  )}
                >
                  <ChevronLeft className="size-5" strokeWidth={1.5} />
                </button>
                <span className="min-w-[5rem] text-center text-[12px] tabular-nums text-subtle">
                  Page {page + 1} of {pageCount}
                </span>
                <button
                  type="button"
                  onClick={() => setPage((p) => p + 1)}
                  disabled={!canNext}
                  aria-label="Next themes"
                  className={cn(
                    "inline-flex size-10 items-center justify-center rounded-full border border-border bg-white transition-colors",
                    canNext
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
      </div>
    </div>
  );
}

function TabButton({
  children,
  active,
  onClick,
}: {
  children: React.ReactNode;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      onClick={onClick}
      className={cn(
        "min-h-[36px] rounded-full px-5 py-1.5 text-[14px] transition-colors",
        active ? "bg-white text-foreground shadow-sm" : "text-subtle hover:text-foreground"
      )}
    >
      {children}
    </button>
  );
}
