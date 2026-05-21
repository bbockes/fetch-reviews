import type { ReportSummary } from "@/lib/types";
import { formatReportDate, reviewAnalysisSummary } from "@/lib/report-utils";

export function ReportHero({ summary }: { summary: ReportSummary }) {
  const appName = summary.app_name ?? `App ${summary.app_id}`;
  const countryCount = Object.keys(summary.storefronts).length;
  const { reviewPhrase, source, regionPhrase } = reviewAnalysisSummary(
    summary.total_reviews,
    countryCount
  );

  return (
    <header className="border-b border-border bg-white pt-6 pb-7 sm:pt-8 sm:pb-8">
      <div className="mx-auto max-w-[1068px] px-6">
        <div className="flex items-end justify-between gap-8 sm:gap-12">
          <h1 className="min-w-0 text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
            {appName}
          </h1>
          {summary.app_url && (
            <a
              href={summary.app_url}
              target="_blank"
              rel="noopener noreferrer"
              className="shrink-0 rounded-full border border-border bg-secondary/60 px-5 py-2.5 text-base text-link transition-colors hover:bg-secondary"
            >
              View App ↗
            </a>
          )}
        </div>
        <p className="mt-6 text-base leading-relaxed text-muted-foreground sm:mt-8 sm:text-lg sm:whitespace-nowrap">
          Analyzed{" "}
          <span className="font-semibold text-foreground">{reviewPhrase}</span> from the{" "}
          <span className="font-semibold text-foreground">{source}</span> spread across{" "}
          <span className="font-semibold text-foreground">{regionPhrase}</span>.
        </p>
        <p className="mt-2 text-base text-muted-foreground">
          Report generated {formatReportDate(summary.generated_at)}
        </p>
      </div>
    </header>
  );
}
