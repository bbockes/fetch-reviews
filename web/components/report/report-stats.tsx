import type { ReportResult } from "@/lib/types";
import { shortenThemeTitle, starShare, topTheme } from "@/lib/report-utils";

export function ReportStats({ report }: { report: ReportResult }) {
  const { summary, loves, pain_points } = report;
  const total = summary.total_reviews;
  const fiveStar = starShare(summary.rating_distribution, 5, total);
  const oneStar = starShare(summary.rating_distribution, 1, total);
  const topLove = topTheme(loves);
  const topPain = topTheme(pain_points);

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <div className="section-muted rounded-2xl p-6 sm:col-span-2 sm:row-span-2 sm:p-8 lg:col-span-2">
        <p className="text-[14px] text-subtle">Average rating</p>
        <p className="text-stat mt-2">{summary.average_rating.toFixed(2)}</p>
        <p className="mt-3 max-w-sm text-[17px] leading-relaxed text-subtle">
          Across {total} written reviews in this sample.
        </p>
      </div>

      <StatCell label="5-star reviews" value={`${fiveStar.pct}%`} detail={`${fiveStar.count} reviews`} />
      <StatCell label="1-star reviews" value={`${oneStar.pct}%`} detail={`${oneStar.count} reviews`} />

      <StatCell
        label="Strongest praise"
        value={topLove ? String(topLove.mention_count) : "—"}
        detail={topLove ? shortenThemeTitle(topLove.title, 36) : "No theme detected"}
        className="sm:col-span-1"
      />
      <StatCell
        label="Biggest friction"
        value={topPain ? String(topPain.mention_count) : "—"}
        detail={topPain ? shortenThemeTitle(topPain.title, 36) : "No theme detected"}
        className="sm:col-span-1"
      />
    </div>
  );
}

function StatCell({
  label,
  value,
  detail,
  className,
}: {
  label: string;
  value: string;
  detail: string;
  className?: string;
}) {
  return (
    <div className={`section-muted rounded-2xl p-6 ${className ?? ""}`}>
      <p className="text-[14px] text-subtle">{label}</p>
      <p className="text-stat mt-2">{value}</p>
      <p className="mt-2 text-[14px] leading-snug text-subtle">{detail}</p>
    </div>
  );
}
