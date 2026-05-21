import type { ReportSummary } from "@/lib/types";

const LOW_DATA_THRESHOLD = 30;

export function ReportLowDataBanner({ summary }: { summary: ReportSummary }) {
  if (summary.total_reviews >= LOW_DATA_THRESHOLD) {
    return null;
  }

  return (
    <div
      className="mx-auto max-w-[1068px] px-6 pb-4"
      role="status"
    >
      <p className="rounded-xl border border-amber-200/80 bg-amber-50 px-5 py-3 text-base leading-relaxed text-amber-950">
        Only {summary.total_reviews} written reviews were found in this sample.
        Themes and takeaways may be limited — results improve as more reviewers
        leave written feedback.
      </p>
    </div>
  );
}
