import type { ReportResult } from "@/lib/types";
import {
  formatAverageRating,
  ratingBarColor,
  ratingInsight,
  storefrontInsight,
  storefrontLabel,
  storefrontMetric,
} from "@/lib/report-utils";

function Card({
  title,
  metric,
  children,
  footer,
}: {
  title: string;
  metric?: React.ReactNode;
  children: React.ReactNode;
  footer?: string;
}) {
  return (
    <div className="rounded-2xl border border-border/80 bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <h3 className="text-[11px] font-semibold uppercase tracking-[0.08em] text-muted-foreground">
          {title}
        </h3>
        {metric && (
          <div className="shrink-0 text-right text-base font-semibold tabular-nums text-foreground sm:text-[17px]">
            {metric}
          </div>
        )}
      </div>
      <div className="mt-5">{children}</div>
      {footer && (
        <p className="mt-6 border-t border-border/60 pt-5 text-base leading-relaxed text-muted-foreground">
          {footer}
        </p>
      )}
    </div>
  );
}

export function ReportData({ report }: { report: ReportResult }) {
  const { summary } = report;
  const total = summary.total_reviews;
  const stars = ["5", "4", "3", "2", "1"];
  const max = Math.max(...stars.map((s) => summary.rating_distribution[s] ?? 0), 1);
  const entries = Object.entries(summary.storefronts).sort(([, a], [, b]) => b - a);
  const sfMax = Math.max(...entries.map(([, c]) => c), 1);
  const avgLabel = formatAverageRating(summary.average_rating);
  const storefrontHeadline = storefrontMetric(summary.storefronts, total);

  return (
    <div className="grid gap-5 lg:grid-cols-2">
      <Card
        title="Rating distribution"
        metric={
          <>
            {avgLabel}
            <span className="text-amber-400"> ★</span>
            <span className="ml-1 text-sm font-medium text-muted-foreground">avg</span>
          </>
        }
        footer={ratingInsight(summary.rating_distribution, total, summary.average_rating)}
      >
        <ul className="space-y-3">
          {stars.map((star) => {
            const count = summary.rating_distribution[star] ?? 0;
            const barPct = (count / max) * 100;
            return (
              <li key={star} className="flex items-center gap-3 text-base">
                <span className="w-6 shrink-0 tabular-nums text-muted-foreground">{star}★</span>
                <div className="h-2 min-w-0 flex-1 overflow-hidden rounded-full bg-secondary">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${barPct}%`,
                      backgroundColor: ratingBarColor(star),
                    }}
                  />
                </div>
                <span className="w-8 shrink-0 text-right tabular-nums text-muted-foreground">
                  {count}
                </span>
              </li>
            );
          })}
        </ul>
      </Card>

      <Card
        title="Reviews by storefront"
        metric={storefrontHeadline || undefined}
        footer={storefrontInsight(summary.storefronts)}
      >
        <ul className="space-y-3">
          {entries.map(([code, count]) => {
            const { name, flag } = storefrontLabel(code);
            const barPct = (count / sfMax) * 100;
            return (
              <li key={code} className="flex items-center gap-3 text-base">
                <span className="flex w-[42%] min-w-0 shrink-0 items-center gap-2 truncate sm:w-[38%]">
                  <span className="text-base leading-none">{flag}</span>
                  <span className="truncate text-foreground">{name}</span>
                </span>
                <div className="h-2 min-w-0 flex-1 overflow-hidden rounded-full bg-secondary">
                  <div
                    className="h-full rounded-full bg-sky-500"
                    style={{ width: `${barPct}%` }}
                  />
                </div>
                <span className="w-8 shrink-0 text-right tabular-nums text-muted-foreground">
                  {count}
                </span>
              </li>
            );
          })}
        </ul>
      </Card>
    </div>
  );
}
