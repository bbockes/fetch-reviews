import type { ReportSummary } from "@/lib/types";
import { formatReportDate, storefrontCodes } from "@/lib/report-utils";

export function ReportHero({ summary }: { summary: ReportSummary }) {
  const regions = storefrontCodes(summary);
  const appName = summary.app_name ?? `App ${summary.app_id}`;

  return (
    <header className="border-b border-border bg-white py-10 sm:py-12">
      <div className="mx-auto flex max-w-[1068px] flex-col gap-6 px-6 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <h1 className="text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
            {appName}
          </h1>
          <p className="mt-2 text-base text-muted-foreground">
            App Store Review Intelligence
            <span className="mx-1.5 text-border">·</span>
            {formatReportDate(summary.generated_at)}
            {regions.length > 0 && (
              <>
                <span className="mx-1.5 text-border">·</span>
                {regions.join(", ")}
              </>
            )}
          </p>
          {summary.one_liner && (
            <p className="mt-4 max-w-2xl text-lg leading-relaxed text-muted-foreground">
              {summary.one_liner}
            </p>
          )}
        </div>

        <div className="flex shrink-0 flex-wrap items-center gap-3">
          <div className="rounded-full border border-border bg-secondary/60 px-5 py-2.5 text-base">
            <span className="font-semibold tabular-nums text-foreground">
              {summary.average_rating.toFixed(2)}
            </span>
            <span className="text-muted-foreground"> avg</span>
            <span className="mx-1.5 text-border">·</span>
            <span className="tabular-nums text-foreground">{summary.total_reviews}</span>
            <span className="text-muted-foreground"> reviews</span>
          </div>
          {summary.app_url && (
            <a
              href={summary.app_url}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-full border border-border bg-secondary/60 px-5 py-2.5 text-base text-link transition-colors hover:bg-secondary"
            >
              App Store ↗
            </a>
          )}
        </div>
      </div>
    </header>
  );
}
