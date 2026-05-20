import type { ReportResult, Theme } from "@/lib/types";

const STOREFRONT_LABELS: Record<string, { name: string; flag: string }> = {
  us: { name: "United States", flag: "🇺🇸" },
  gb: { name: "Great Britain", flag: "🇬🇧" },
  ca: { name: "Canada", flag: "🇨🇦" },
  au: { name: "Australia", flag: "🇦🇺" },
  nz: { name: "New Zealand", flag: "🇳🇿" },
  ie: { name: "Ireland", flag: "🇮🇪" },
};

const RATING_BAR_COLORS: Record<string, string> = {
  "5": "#141414",
  "4": "#404040",
  "3": "#707070",
  "2": "#aaaaaa",
  "1": "#c2c2c2",
};

export function formatReportDate(iso: string) {
  try {
    return new Date(iso).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return new Date().toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  }
}

export function storefrontLabel(code: string) {
  const key = code.toLowerCase();
  return STOREFRONT_LABELS[key] ?? { name: code.toUpperCase(), flag: "🌐" };
}

export function storefrontCodes(summary: ReportResult["summary"]) {
  return Object.keys(summary.storefronts)
    .sort((a, b) => summary.storefronts[b] - summary.storefronts[a])
    .map((c) => c.toUpperCase());
}

export function ratingBarColor(star: string) {
  return RATING_BAR_COLORS[star] ?? "#71717a";
}

export function starShare(
  distribution: Record<string, number>,
  star: number,
  total: number
) {
  const count = distribution[String(star)] ?? 0;
  const pct = total ? Math.round((count / total) * 100) : 0;
  return { count, pct };
}

export function shortenThemeTitle(title: string, max = 28) {
  if (title.length <= max) return title;
  return title.slice(0, max - 1).trim() + "…";
}

export function parseTakeaway(text: string): { title: string; body: string } {
  const dash = text.indexOf(" — ");
  if (dash !== -1) {
    return {
      title: text.slice(0, dash).trim(),
      body: text.slice(dash + 3).trim(),
    };
  }
  const idx = text.indexOf(":");
  if (idx === -1) return { title: text, body: "" };
  return {
    title: text.slice(0, idx).trim(),
    body: text.slice(idx + 1).trim(),
  };
}

/** Semantic tone for highlights & takeaways — mirrors love / pain / insight */
export type ReportTone = "love" | "pain" | "insight";

export function classifyTakeaway(text: string): ReportTone {
  const lower = text.toLowerCase();
  const pain =
    /\b(fix|fixing|complaint|complaints|pain point|address|below|issue|issues|problem|friction|prioritize|risk|broken|bug)\b/.test(
      lower
    );
  const strength =
    /\b(praise|strongest|love|lead with|marketing|onboarding|enthusiasm|champion|double down|highlight)\b/.test(
      lower
    );

  if (strength && !pain) return "love";
  if (pain) return "pain";
  return "insight";
}

export function topTheme(themes: Theme[]) {
  if (!themes.length) return null;
  return themes.reduce((a, b) => (b.mention_count > a.mention_count ? b : a));
}

export function ratingInsight(distribution: Record<string, number>, total: number) {
  const five = distribution["5"] ?? 0;
  const one = distribution["1"] ?? 0;
  const mid = (distribution["3"] ?? 0) + (distribution["2"] ?? 0);
  if (five > one * 2)
    return "Sentiment skews positive at the top end, but a sizable 1★ cohort keeps the average below 4★.";
  if (one > five)
    return "Negative reviews are loud enough to drag perception — pain themes deserve priority.";
  if (mid > total * 0.3)
    return "Many 2–3★ reviews suggest interest without full satisfaction — fix expectation gaps.";
  return "Ratings are spread across the scale — positioning clarity will matter for conversion.";
}

export function storefrontInsight(storefronts: Record<string, number>) {
  const entries = Object.entries(storefronts).sort(([, a], [, b]) => b - a);
  if (entries.length <= 1) return "Most written reviews in this sample come from a single storefront.";
  const [top, second] = entries;
  if (top[1] > (second?.[1] ?? 0) * 3)
    return `${top[0].toUpperCase()} dominates the sample; international voices add pricing and trust themes.`;
  return "Multiple storefronts contribute — compare regional themes before global messaging changes.";
}
