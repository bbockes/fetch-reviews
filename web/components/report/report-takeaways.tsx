import { ReportIcon, takeawayIcon } from "@/components/report/highlight-icon";
import { classifyTakeaway, parseTakeaway } from "@/lib/report-utils";

export function ReportTakeaways({ takeaways }: { takeaways: string[] }) {
  const items = takeaways.slice(0, 6);
  if (!items.length) return null;

  const toneCounts: Record<string, number> = { love: 0, pain: 0, insight: 0 };

  return (
    <div className="grid gap-5 sm:grid-cols-2">
      {items.map((text, i) => {
        const { title, body } = parseTakeaway(text);
        const tone = classifyTakeaway(text);
        const iconIndex = toneCounts[tone]++;
        const Icon = takeawayIcon(tone, iconIndex);

        return (
          <article
            key={i}
            className="flex gap-5 rounded-2xl border border-border/70 bg-white p-6 shadow-sm"
          >
            <ReportIcon icon={Icon} tone={tone} />
            <div className="min-w-0 pt-0.5">
              <h3 className="text-lg font-semibold leading-snug text-foreground">{title}</h3>
              {body && (
                <p className="mt-2 text-base leading-relaxed text-muted-foreground">{body}</p>
              )}
            </div>
          </article>
        );
      })}
    </div>
  );
}
