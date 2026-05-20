import {
  BookOpen,
  ClipboardList,
  Database,
  DollarSign,
  Flag,
  Search,
  Target,
} from "lucide-react";

import { ThemesSection } from "@/components/report/themes-section";
import type { ReportResult } from "@/lib/types";
import {
  formatReportDate,
  parseTakeaway,
  ratingBarColor,
  ratingInsight,
  shortenThemeTitle,
  starShare,
  storefrontInsight,
  storefrontLabel,
  storefrontCodes,
  topTheme,
} from "@/lib/report-utils";

const TAKEAWAY_ICONS = [Target, ClipboardList, Database, DollarSign, Search, Flag];

function SectionLabel({ children }: { children: React.ReactNode }) {
  return <h2 className="text-label">{children}</h2>;
}

function MetricCard({
  label,
  value,
  sub,
}: {
  label: string;
  value: string;
  sub: string;
}) {
  return (
    <div className="rounded-3xl bg-card px-6 py-6 shadow-card ring-1 ring-border/50">
      <p className="text-xs font-medium text-muted-foreground">{label}</p>
      <p className="mt-2 text-3xl font-semibold tracking-[-0.03em] tabular-nums text-foreground">
        {value}
      </p>
      <p className="mt-1.5 text-sm leading-snug text-muted-foreground">{sub}</p>
    </div>
  );
}

function RatingDistribution({
  distribution,
  total,
}: {
  distribution: Record<string, number>;
  total: number;
}) {
  const stars = ["5", "4", "3", "2", "1"];
  const max = Math.max(...stars.map((s) => distribution[s] ?? 0), 1);

  return (
    <div className="rounded-3xl bg-card p-6 shadow-card ring-1 ring-border/50 sm:p-8">
      <SectionLabel>Rating distribution</SectionLabel>
      <ul className="mt-6 space-y-3">
        {stars.map((star) => {
          const count = distribution[star] ?? 0;
          const pct = (count / max) * 100;
          return (
            <li key={star} className="flex items-center gap-4 text-sm">
              <span className="w-8 shrink-0 font-medium tabular-nums text-muted-foreground">
                {star}★
              </span>
              <div className="h-2 min-w-0 flex-1 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${pct}%`,
                    backgroundColor: ratingBarColor(star),
                  }}
                />
              </div>
              <span className="w-8 shrink-0 text-right text-sm tabular-nums text-muted-foreground">
                {count}
              </span>
            </li>
          );
        })}
      </ul>
      <p className="mt-6 text-sm leading-relaxed text-muted-foreground">
        {ratingInsight(distribution, total)}
      </p>
    </div>
  );
}

function StorefrontChart({ storefronts }: { storefronts: Record<string, number> }) {
  const entries = Object.entries(storefronts).sort(([, a], [, b]) => b - a);
  const max = Math.max(...entries.map(([, c]) => c), 1);

  return (
    <div className="rounded-3xl bg-card p-6 shadow-card ring-1 ring-border/50 sm:p-8">
      <SectionLabel>Reviews by storefront</SectionLabel>
      <ul className="mt-6 space-y-3">
        {entries.map(([code, count]) => {
          const { name, flag } = storefrontLabel(code);
          const pct = (count / max) * 100;
          return (
            <li key={code} className="flex items-center gap-4 text-sm">
              <span className="flex w-[44%] shrink-0 items-center gap-2 truncate text-foreground sm:w-[40%]">
                <span className="text-base leading-none">{flag}</span>
                <span className="truncate font-medium">{name}</span>
              </span>
              <div className="h-2 min-w-0 flex-1 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-brand transition-all duration-500"
                  style={{ width: `${pct}%` }}
                />
              </div>
              <span className="w-8 shrink-0 text-right text-sm tabular-nums text-muted-foreground">
                {count}
              </span>
            </li>
          );
        })}
      </ul>
      <p className="mt-6 text-sm leading-relaxed text-muted-foreground">
        {storefrontInsight(storefronts)}
      </p>
    </div>
  );
}

export function ReportView({ report }: { report: ReportResult }) {
  const { summary, loves, pain_points, takeaways } = report;
  const total = summary.total_reviews;
  const fiveStar = starShare(summary.rating_distribution, 5, total);
  const oneStar = starShare(summary.rating_distribution, 1, total);
  const topLove = topTheme(loves);
  const topPain = topTheme(pain_points);
  const regions = storefrontCodes(summary);

  return (
    <article
      className="mx-auto space-y-8 px-6 py-10 sm:space-y-10 sm:py-14"
      style={{ maxWidth: "var(--max-content-width)" }}
    >
      <header className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex gap-5">
          <div className="flex size-14 shrink-0 items-center justify-center rounded-2xl bg-foreground">
            <BookOpen className="size-7 text-background" strokeWidth={1.75} />
          </div>
          <div>
            <h1 className="text-headline text-2xl sm:text-3xl">
              {summary.app_name ?? `App ${summary.app_id}`}
            </h1>
            <p className="mt-2 text-sm text-muted-foreground">
              App Store Review Intelligence
              <span className="mx-2 text-border">·</span>
              {formatReportDate(summary.generated_at)}
              {regions.length > 0 && (
                <>
                  <span className="mx-2 text-border">·</span>
                  {regions.join(", ")}
                </>
              )}
            </p>
          </div>
        </div>
        <div className="inline-flex shrink-0 items-center gap-1 rounded-full bg-secondary px-5 py-2.5 text-sm">
          <span className="font-semibold tabular-nums text-foreground">
            {summary.average_rating.toFixed(2)}
          </span>
          <span className="text-muted-foreground">avg</span>
          <span className="mx-1 text-border">·</span>
          <span className="font-semibold tabular-nums text-foreground">{total}</span>
          <span className="text-muted-foreground">reviews</span>
        </div>
      </header>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <MetricCard
          label="5-star share"
          value={`${fiveStar.pct}%`}
          sub={`${fiveStar.count} of ${total} reviews`}
        />
        <MetricCard
          label="1-star share"
          value={`${oneStar.pct}%`}
          sub={`${oneStar.count} of ${total} reviews`}
        />
        <MetricCard
          label="Top love theme"
          value={topLove ? String(topLove.mention_count) : "—"}
          sub={topLove ? shortenThemeTitle(topLove.title) : "None detected"}
        />
        <MetricCard
          label="Top pain theme"
          value={topPain ? String(topPain.mention_count) : "—"}
          sub={topPain ? shortenThemeTitle(topPain.title) : "None detected"}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <RatingDistribution
          distribution={summary.rating_distribution}
          total={total}
        />
        <StorefrontChart storefronts={summary.storefronts} />
      </div>

      <ThemesSection loves={loves} painPoints={pain_points} />

      <section>
        <SectionLabel>Strategic takeaways</SectionLabel>
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          {takeaways.slice(0, 6).map((text, i) => {
            const { title, body } = parseTakeaway(text);
            const Icon = TAKEAWAY_ICONS[i % TAKEAWAY_ICONS.length];
            return (
              <div
                key={i}
                className="rounded-3xl bg-card p-6 shadow-card ring-1 ring-border/50"
              >
                <div className="flex items-start gap-4">
                  <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-secondary text-muted-foreground">
                    <Icon className="size-4" strokeWidth={1.75} />
                  </div>
                  <div className="min-w-0">
                    <h3 className="text-[15px] font-semibold tracking-[-0.01em] text-foreground">
                      {title}
                    </h3>
                    {body && (
                      <p className="mt-2.5 text-sm leading-relaxed text-muted-foreground">
                        {body}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      <p className="pt-6 text-center text-xs text-muted-foreground">
        Report generated from public App Store written-review feeds. Not affiliated with Apple.
      </p>
    </article>
  );
}
