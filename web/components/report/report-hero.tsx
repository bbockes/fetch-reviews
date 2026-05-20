import type { ReportSummary } from "@/lib/types";
import { formatReportDate, storefrontCodes } from "@/lib/report-utils";

export function ReportHero({ summary }: { summary: ReportSummary }) {
  const regions = storefrontCodes(summary);
  const appName = summary.app_name ?? `App ${summary.app_id}`;

  return (
    <header className="section-pad pb-12 pt-10 text-center sm:pb-16 sm:pt-14">
      <div className="container-apple">
        <p className="text-eyebrow">Review report</p>
        <h1 className="text-hero mt-3 text-balance">{appName}</h1>
        {summary.one_liner && (
          <p className="text-hero-sub mx-auto mt-5 max-w-2xl text-pretty">{summary.one_liner}</p>
        )}

        <dl className="mx-auto mt-8 inline-flex flex-wrap items-center justify-center gap-x-4 gap-y-2 text-[14px] text-subtle sm:text-[17px]">
          <div className="flex items-baseline gap-1.5">
            <dt className="sr-only">Average rating</dt>
            <dd className="font-semibold tabular-nums text-foreground">
              {summary.average_rating.toFixed(2)}
            </dd>
            <span>average</span>
          </div>
          <span className="hidden text-border sm:inline" aria-hidden>
            |
          </span>
          <div>
            <dt className="sr-only">Total reviews</dt>
            <dd>
              <span className="font-semibold tabular-nums text-foreground">
                {summary.total_reviews}
              </span>{" "}
              reviews
            </dd>
          </div>
          <span className="hidden text-border sm:inline" aria-hidden>
            |
          </span>
          <div>
            <dt className="sr-only">Generated</dt>
            <dd>{formatReportDate(summary.generated_at)}</dd>
          </div>
          {regions.length > 0 && (
            <>
              <span className="hidden text-border sm:inline" aria-hidden>
                |
              </span>
              <div>
                <dt className="sr-only">Regions</dt>
                <dd>{regions.join(" · ")}</dd>
              </div>
            </>
          )}
        </dl>

        {summary.app_url && (
          <p className="mt-6">
            <a
              href={summary.app_url}
              target="_blank"
              rel="noopener noreferrer"
              className="link-apple text-[14px]"
            >
              View on the App Store ↗
            </a>
          </p>
        )}
      </div>
    </header>
  );
}
