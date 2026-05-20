import { parseTakeaway } from "@/lib/report-utils";

export function ReportTakeaways({ takeaways }: { takeaways: string[] }) {
  const items = takeaways.slice(0, 6);
  if (!items.length) return null;

  return (
    <div className="space-y-0">
      {items.map((text, i) => {
        const { title, body } = parseTakeaway(text);
        return (
          <article key={i} className="border-b border-border py-8 first:pt-0 last:border-b-0 last:pb-0">
            <h3 className="text-[21px] font-semibold tracking-[-0.02em] text-foreground">
              {title}
            </h3>
            {body && (
              <p className="mt-3 text-[17px] leading-relaxed text-subtle">{body}</p>
            )}
          </article>
        );
      })}
    </div>
  );
}
