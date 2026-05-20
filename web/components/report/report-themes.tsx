"use client";

import { AlertTriangle, Heart } from "lucide-react";
import { useEffect, useState } from "react";

import { ReportCard } from "@/components/report/report-section";
import { ICON_STROKE } from "@/components/report/highlight-icon";
import { ThemeItem } from "@/components/report/theme-item";
import type { Theme } from "@/lib/types";
import { cn } from "@/lib/utils";

export function ReportThemes({
  loves,
  painPoints,
}: {
  loves: Theme[];
  painPoints: Theme[];
}) {
  const [mode, setMode] = useState<"love" | "pain">("love");
  const [openThemeTitle, setOpenThemeTitle] = useState<string | null>(null);
  const themes = mode === "love" ? loves : painPoints;
  const maxCount = Math.max(...themes.map((t) => t.mention_count), 1);

  useEffect(() => {
    setOpenThemeTitle(null);
  }, [mode]);

  return (
    <ReportCard className="!p-0 sm:!p-0">
      <div className="border-b border-border/70 px-6 py-4 sm:px-8">
        <div className="flex flex-wrap gap-2">
          <TabButton active={mode === "love"} onClick={() => setMode("love")} variant="love">
            <Heart className="size-4" strokeWidth={ICON_STROKE} />
            What they love
          </TabButton>
          <TabButton active={mode === "pain"} onClick={() => setMode("pain")} variant="pain">
            <AlertTriangle className="size-4" strokeWidth={ICON_STROKE} />
            Pain points
          </TabButton>
        </div>
      </div>

      <div className="px-4 py-1 sm:px-6" role="tabpanel">
        {themes.length === 0 ? (
          <p className="py-12 text-center text-sm text-muted-foreground">
            No themes in this category.
          </p>
        ) : (
          <ul>
            {themes.map((theme) => (
              <ThemeItem
                key={theme.title}
                theme={theme}
                variant={mode}
                maxCount={maxCount}
                open={openThemeTitle === theme.title}
                onToggle={() =>
                  setOpenThemeTitle((current) =>
                    current === theme.title ? null : theme.title
                  )
                }
              />
            ))}
          </ul>
        )}
      </div>
    </ReportCard>
  );
}

function TabButton({
  children,
  active,
  onClick,
  variant,
}: {
  children: React.ReactNode;
  active: boolean;
  onClick: () => void;
  variant: "love" | "pain";
}) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-2 rounded-full px-5 py-2.5 text-base font-medium transition-colors",
        active
          ? variant === "love"
            ? "bg-emerald-100 text-emerald-900"
            : "bg-red-100 text-red-900"
          : "text-muted-foreground hover:bg-secondary hover:text-foreground"
      )}
    >
      {children}
    </button>
  );
}
