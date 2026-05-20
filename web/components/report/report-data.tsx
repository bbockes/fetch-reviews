import type { ReportResult } from "@/lib/types";
import {
  ratingBarColor,
  ratingInsight,
  storefrontInsight,
  storefrontLabel,
} from "@/lib/report-utils";

export function ReportData({ report }: { report: ReportResult }) {
  const { summary } = report;
  const total = summary.total_reviews;
  const stars = ["5", "4", "3", "2", "1"];
  const max = Math.max(...stars.map((s) => summary.rating_distribution[s] ?? 0), 1);
  const entries = Object.entries(summary.storefronts).sort(([, a], [, b]) => b - a);

  return (
    <div className="grid gap-12 lg:grid-cols-2 lg:gap-16">
      <div>
        <h3 className="text-[21px] font-semibold tracking-[-0.02em]">Star ratings</h3>
        <ul className="mt-6 space-y-4">
          {stars.map((star) => {
            const count = summary.rating_distribution[star] ?? 0;
            const pctOfTotal = total ? Math.round((count / total) * 100) : 0;
            const barPct = (count / max) * 100;
            return (
              <li key={star}>
                <div className="mb-1.5 flex justify-between text-[14px]">
                  <span className="text-foreground">{star} stars</span>
                  <span className="tabular-nums text-subtle">
                    {pctOfTotal}% <span className="text-border">·</span> {count}
                  </span>
                </div>
                <div className="h-1 overflow-hidden rounded-full bg-border/60">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${barPct}%`,
                      backgroundColor: ratingBarColor(star),
                    }}
                  />
                </div>
              </li>
            );
          })}
        </ul>
        <p className="mt-6 text-[14px] leading-relaxed text-subtle">
          {ratingInsight(summary.rating_distribution, total)}
        </p>
      </div>

      <div>
        <h3 className="text-[21px] font-semibold tracking-[-0.02em]">By storefront</h3>
        <ul className="mt-6 divide-y divide-border">
          {entries.map(([code, count]) => {
            const { name, flag } = storefrontLabel(code);
            const pct = total ? Math.round((count / total) * 100) : 0;
            return (
              <li
                key={code}
                className="flex items-center justify-between gap-4 py-3.5 text-[17px] first:pt-0"
              >
                <span className="flex min-w-0 items-center gap-2">
                  <span className="text-lg leading-none">{flag}</span>
                  <span className="truncate">{name}</span>
                </span>
                <span className="shrink-0 tabular-nums text-subtle">
                  {pct}% <span className="text-border">·</span> {count}
                </span>
              </li>
            );
          })}
        </ul>
        <p className="mt-6 text-[14px] leading-relaxed text-subtle">
          {storefrontInsight(summary.storefronts)}
        </p>
      </div>
    </div>
  );
}
