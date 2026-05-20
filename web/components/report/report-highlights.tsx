import type { ReportResult } from "@/lib/types";
import { HIGHLIGHT_ITEMS, ReportIcon } from "@/components/report/highlight-icon";
import { shortenThemeTitle, starShare, topFeatureTheme, topTheme } from "@/lib/report-utils";

type HighlightItem = {
  key: string;
  icon: (typeof HIGHLIGHT_ITEMS)[number]["icon"];
  tone: (typeof HIGHLIGHT_ITEMS)[number]["tone"];
  label?: string;
  title: string;
  subtitle?: string;
};

export function ReportHighlights({ report }: { report: ReportResult }) {
  const { summary, loves, pain_points } = report;
  const total = summary.total_reviews;
  const fiveStar = starShare(summary.rating_distribution, 5, total);
  const oneStar = starShare(summary.rating_distribution, 1, total);
  const topLove = topFeatureTheme(loves);
  const topPain = topTheme(pain_points);

  const items: HighlightItem[] = [
    {
      ...HIGHLIGHT_ITEMS[0],
      key: "five-star",
      title: `${fiveStar.pct}% of reviewers rated 5 stars`,
      subtitle: `${fiveStar.count} of ${total} reviews`,
    },
    {
      ...HIGHLIGHT_ITEMS[1],
      key: "one-star",
      title: `${oneStar.pct}% of reviewers rated 1 star`,
      subtitle: `${oneStar.count} of ${total} reviews`,
    },
    {
      ...HIGHLIGHT_ITEMS[2],
      key: "praise",
      label: topLove ? "Most loved feature" : undefined,
      title: topLove ? shortenThemeTitle(topLove.title, 56) : "No feature praise detected",
      subtitle: topLove ? `${topLove.mention_count} mentions` : undefined,
    },
    {
      ...HIGHLIGHT_ITEMS[3],
      key: "complaint",
      label: topPain ? "Biggest complaint" : undefined,
      title: topPain ? shortenThemeTitle(topPain.title, 56) : "No pain theme detected",
      subtitle: topPain ? `${topPain.mention_count} mentions` : undefined,
    },
  ];

  return (
    <div className="grid gap-10 sm:grid-cols-2 sm:gap-x-14 sm:gap-y-10">
      {items.map((item) => (
        <article key={item.key} className="flex gap-5">
          <ReportIcon icon={item.icon} tone={item.tone} size="lg" />
          <div className="min-w-0 pt-1">
            {item.label && (
              <p className="text-sm font-medium text-muted-foreground">{item.label}</p>
            )}
            <h3
              className={`text-lg font-semibold leading-snug text-foreground ${item.label ? "mt-1" : ""}`}
            >
              {item.title}
            </h3>
            {item.subtitle && (
              <p className="mt-1.5 text-base leading-snug text-muted-foreground">{item.subtitle}</p>
            )}
          </div>
        </article>
      ))}
    </div>
  );
}
