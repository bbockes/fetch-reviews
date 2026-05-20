import type { ReportResult } from "@/lib/types";
import { HIGHLIGHT_ITEMS, ReportIcon } from "@/components/report/highlight-icon";
import { shortenThemeTitle, starShare, topTheme } from "@/lib/report-utils";

export function ReportHighlights({ report }: { report: ReportResult }) {
  const { summary, loves, pain_points } = report;
  const total = summary.total_reviews;
  const fiveStar = starShare(summary.rating_distribution, 5, total);
  const oneStar = starShare(summary.rating_distribution, 1, total);
  const topLove = topTheme(loves);
  const topPain = topTheme(pain_points);

  const items = [
    {
      ...HIGHLIGHT_ITEMS[0],
      title: `${fiveStar.count} of ${total} reviews rated 5 stars`,
      subtitle: `${fiveStar.pct}% of reviewers`,
    },
    {
      ...HIGHLIGHT_ITEMS[1],
      title: `${oneStar.count} of ${total} reviews rated 1 star`,
      subtitle: `${oneStar.pct}% of reviewers`,
    },
    {
      ...HIGHLIGHT_ITEMS[2],
      title: topLove
        ? `${topLove.mention_count} mentions — ${shortenThemeTitle(topLove.title, 48)}`
        : "No praise theme detected",
      subtitle: topLove ? "Most cited reason users love the app" : undefined,
    },
    {
      ...HIGHLIGHT_ITEMS[3],
      title: topPain
        ? `${topPain.mention_count} mentions — ${shortenThemeTitle(topPain.title, 48)}`
        : "No pain theme detected",
      subtitle: topPain ? "Most cited friction in written reviews" : undefined,
    },
  ];

  return (
    <div className="grid gap-10 sm:grid-cols-2 sm:gap-x-14 sm:gap-y-10">
      {items.map((item) => (
        <article key={item.title} className="flex gap-5">
          <ReportIcon icon={item.icon} tone={item.tone} size="lg" />
          <div className="min-w-0 pt-1">
            <h3 className="text-lg font-semibold leading-snug text-foreground">{item.title}</h3>
            {item.subtitle && (
              <p className="mt-1.5 text-base leading-snug text-muted-foreground">{item.subtitle}</p>
            )}
          </div>
        </article>
      ))}
    </div>
  );
}
