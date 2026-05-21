"use client";

import { AlertTriangle, ChevronDown, Lightbulb, TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";

import { ICON_STROKE, TONE_STYLES } from "@/components/report/highlight-icon";
import { ReportCard } from "@/components/report/report-section";
import {
  groupTakeawaysByCategory,
  normalizeTakeaways,
  TAKEAWAY_SECTIONS,
  takeawayDisplay,
} from "@/lib/report-utils";
import type { Takeaway, TakeawayCategory } from "@/lib/types";
import { cn } from "@/lib/utils";

const SECTION_ICON = {
  strength: TrendingUp,
  fix: AlertTriangle,
  opportunity: Lightbulb,
} as const;

const CHEVRON_OPEN = "bg-zinc-600";

function takeawayKey(item: Takeaway) {
  return `${item.category}:${item.title}`;
}

function TakeawayItem({
  item,
  open,
  onToggle,
}: {
  item: Takeaway;
  open: boolean;
  onToggle: () => void;
}) {
  const { summary, points } = takeawayDisplay(item);

  return (
    <li className="border-b border-border/60 last:border-b-0">
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        className={cn(
          "flex w-full cursor-pointer items-center gap-3 bg-white py-4 text-left transition-colors",
          !open && "hover:bg-secondary/40"
        )}
      >
        <span className="min-w-0 flex-1 text-base font-medium leading-snug text-foreground sm:text-[17px]">
          {item.title}
        </span>
        <span className="relative grid size-7 shrink-0 place-items-center">
          <span
            className={cn(
              "absolute inset-0 rounded-full transition-opacity duration-200",
              open ? cn(CHEVRON_OPEN, "opacity-100") : "opacity-0"
            )}
            aria-hidden
          />
          <ChevronDown
            className={cn(
              "relative z-[1] size-4 transition-transform duration-200",
              open ? "rotate-180 text-white" : "text-muted-foreground"
            )}
            aria-hidden
          />
        </span>
      </button>

      {open && (
        <div className="border-t border-border/60 bg-white pb-5 pt-4">
          {summary && (
            <p className="text-base font-semibold leading-relaxed text-foreground sm:text-[17px]">
              {summary}
            </p>
          )}
          {points.length > 0 && (
            <ul className="mt-3 list-disc space-y-1.5 pl-5 text-base leading-relaxed text-foreground sm:text-[17px]">
              {points.map((point, i) => (
                <li key={i}>{point}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </li>
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
  variant: TakeawayCategory;
}) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-2 rounded-full border-0 px-5 py-2.5 text-base font-medium transition-colors outline-none",
        active
          ? variant === "strength"
            ? "bg-emerald-100 text-emerald-900"
            : variant === "fix"
              ? "bg-red-100 text-red-900"
              : "bg-sky-100 text-sky-900"
          : "text-muted-foreground hover:bg-secondary hover:text-foreground"
      )}
    >
      {children}
    </button>
  );
}

export function ReportTakeaways({ takeaways }: { takeaways: Takeaway[] | string[] }) {
  const items = normalizeTakeaways(takeaways);
  const grouped = groupTakeawaysByCategory(items);
  const visibleSections = TAKEAWAY_SECTIONS.filter(
    (section) => grouped[section.category].length > 0
  );

  const [category, setCategory] = useState<TakeawayCategory>(
    () => visibleSections[0]?.category ?? "strength"
  );
  const [openKey, setOpenKey] = useState<string | null>(null);

  useEffect(() => {
    setOpenKey(null);
  }, [category]);

  useEffect(() => {
    if (!visibleSections.some((section) => section.category === category)) {
      setCategory(visibleSections[0]?.category ?? "strength");
    }
  }, [category, visibleSections]);

  if (!visibleSections.length) return null;

  const cards = grouped[category];

  return (
    <ReportCard className="!p-0 sm:!p-0">
      <div className="border-b border-border/70 px-6 py-4 sm:px-8">
        <div className="flex flex-wrap gap-2" role="tablist">
          {visibleSections.map((section) => {
            const SectionIcon = SECTION_ICON[section.category];
            const toneStyles = TONE_STYLES[section.tone];
            return (
              <TabButton
                key={section.category}
                active={category === section.category}
                onClick={() => setCategory(section.category)}
                variant={section.category}
              >
                <SectionIcon
                  className={cn(
                    "size-4",
                    category === section.category ? undefined : toneStyles.icon
                  )}
                  strokeWidth={ICON_STROKE}
                />
                {section.label}
              </TabButton>
            );
          })}
        </div>
      </div>

      <div className="px-4 py-1 sm:px-6" role="tabpanel">
        {cards.length === 0 ? (
          <p className="py-12 text-center text-sm text-muted-foreground">
            No recommendations in this category.
          </p>
        ) : (
          <ul>
            {cards.map((item) => {
              const key = takeawayKey(item);
              return (
                <TakeawayItem
                  key={key}
                  item={item}
                  open={openKey === key}
                  onToggle={() =>
                    setOpenKey((current) => (current === key ? null : key))
                  }
                />
              );
            })}
          </ul>
        )}
      </div>
    </ReportCard>
  );
}
