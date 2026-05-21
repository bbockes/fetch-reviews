import type { ReportResult, Takeaway, TakeawayCategory, Theme } from "@/lib/types";

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

/** Hero summary copy — keep in sync with backend build_review_analysis_one_liner */
export function reviewAnalysisSummary(totalReviews: number, countryCount: number) {
  const countryLabel = countryCount === 1 ? "Country" : "Countries";
  const reviewPhrase = `${totalReviews} written reviews`;
  const source = "App Store";
  const regionPhrase = `${countryCount} ${countryLabel}`;

  return {
    reviewPhrase,
    source,
    regionPhrase,
    plain: `Analyzed ${reviewPhrase} from the ${source} spread across ${regionPhrase}.`,
  };
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

function capitalizeFirst(text: string): string {
  const trimmed = text.trim();
  if (!trimmed) return trimmed;
  return trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
}

export function parseTakeaway(text: string): { title: string; body: string } {
  const dash = text.indexOf(" — ");
  if (dash !== -1) {
    return {
      title: text.slice(0, dash).trim(),
      body: capitalizeFirst(text.slice(dash + 3)),
    };
  }
  const idx = text.indexOf(":");
  if (idx === -1) return { title: text, body: "" };
  return {
    title: text.slice(0, idx).trim(),
    body: capitalizeFirst(text.slice(idx + 1)),
  };
}

/** Semantic tone for highlights & takeaways — mirrors love / pain / insight */
export type ReportTone = "love" | "pain" | "insight";

export const TAKEAWAY_SECTIONS: {
  category: TakeawayCategory;
  label: string;
  tone: ReportTone;
}[] = [
  { category: "strength", label: "Build on what works", tone: "love" },
  { category: "fix", label: "Fix what doesn't", tone: "pain" },
  { category: "opportunity", label: "Go further", tone: "insight" },
];

export function takeawayCategoryTone(category: TakeawayCategory): ReportTone {
  const section = TAKEAWAY_SECTIONS.find((s) => s.category === category);
  return section?.tone ?? "insight";
}

/** Accept structured takeaways or legacy "title — body" strings from older reports. */
export function normalizeTakeaways(raw: Takeaway[] | string[]): Takeaway[] {
  if (!raw.length) return [];
  if (typeof raw[0] !== "string") return raw as Takeaway[];

  return (raw as string[]).map((text) => {
    const parsed = parseTakeaway(text);
    return {
      title: parsed.title,
      body: parsed.body,
      category: legacyTakeawayCategory(text),
    };
  });
}

function legacyTakeawayCategory(text: string): TakeawayCategory {
  const lower = text.toLowerCase();
  if (
    /\b(marketing copy|highlight|lead with|lead your|showcase|show how|helps at|helps during|ask for a review)\b/.test(
      lower
    ) &&
    !/\b(too expensive|missing|not indexed|paywall|complaint|misleading|deceptive)\b/.test(
      lower
    )
  ) {
    return "strength";
  }
  if (/\b(same workflow|share one|both groups|one focused|go further|overlap)\b/.test(lower)) {
    return "opportunity";
  }
  const tone = classifyTakeaway(text);
  if (tone === "love") return "strength";
  if (tone === "pain") return "fix";
  return "opportunity";
}

export function groupTakeawaysByCategory(items: Takeaway[]): Record<TakeawayCategory, Takeaway[]> {
  const grouped: Record<TakeawayCategory, Takeaway[]> = {
    strength: [],
    fix: [],
    opportunity: [],
  };
  for (const item of items) {
    if (grouped[item.category]) {
      grouped[item.category].push(item);
    }
  }
  return grouped;
}

/** Remove a stray period after a closing quote when the quote already ends with one. */
export function normalizeTakeawayPunctuation(text: string): string {
  return text.replace(/(['"])([^'"]*\.)\1\./g, "$1$2$1");
}

/** Structured summary + bullets; splits legacy body when summary/points absent. */
export function takeawayDisplay(item: Takeaway): { summary: string; points: string[] } {
  const summary = item.summary?.trim();
  const points = (item.points ?? []).map((p) => p.trim()).filter(Boolean);
  if (summary) {
    return {
      summary: normalizeTakeawayPunctuation(summary),
      points: points.map(normalizeTakeawayPunctuation),
    };
  }

  const body = item.body?.trim() ?? "";
  if (!body) return { summary: "", points: [] };

  const cleaned = normalizeTakeawayPunctuation(body);
  const sentences = cleaned.match(/[^.!?]+[.!?]+(?:\s|$)|[^.!?]+$/g) ?? [cleaned];
  const trimmed = sentences.map((s) => s.trim()).filter(Boolean);
  if (trimmed.length <= 1) {
    return { summary: trimmed[0] ?? cleaned, points: [] };
  }
  return { summary: trimmed[0], points: trimmed.slice(1) };
}

export function classifyTakeaway(text: string): ReportTone {
  const lower = text.toLowerCase();
  const pain =
    /\b(fix|fixing|sprint|complaint|complaints|pain point|address|below|expectation|funnel|issue|issues|problem|friction|prioritize|risk|broken|bug)\b/.test(
      lower
    );
  const strength =
    /\b(praise|strongest|love|lead with|lead your|uvp|uvps|marketing|onboarding|value moment|satisfaction|double down|highlight|rewrite|strongest)\b/.test(
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

const GENERIC_PRAISE_TITLE =
  /enthusiasm|game.?changer|generic praise|what delighted|overall love|amazing app|best app|love this app|users love|strong praise/i;

const GENERIC_PAIN_TITLE =
  /common complaint|generic|overall hate|terrible app|hate this app|worst app|users hate|strong complaint|overall frustration|what hurts/i;

export function isFeatureLoveTheme(theme: Theme) {
  return !GENERIC_PRAISE_TITLE.test(theme.title);
}

export function isFeaturePainTheme(theme: Theme) {
  return !GENERIC_PAIN_TITLE.test(theme.title);
}

export function filterFeatureLoves(themes: Theme[]) {
  return themes.filter(isFeatureLoveTheme);
}

export function filterFeaturePains(themes: Theme[]) {
  return themes.filter(isFeaturePainTheme);
}

/** Top praise theme that names a concrete product feature — not generic enthusiasm. */
export function topFeatureTheme(themes: Theme[]) {
  return topTheme(filterFeatureLoves(themes));
}

export function formatAverageRating(avg: number): string {
  return avg.toFixed(1);
}

export function ratingInsight(
  distribution: Record<string, number>,
  total: number,
  averageRating: number
) {
  const avg = formatAverageRating(averageRating);
  const five = distribution["5"] ?? 0;
  const one = distribution["1"] ?? 0;
  const mid = (distribution["3"] ?? 0) + (distribution["2"] ?? 0);
  if (five > one * 2)
    return `Sentiment skews positive at the top end, but a sizable one-star cohort keeps the sample average at ${avg} stars.`;
  if (one > five)
    return `Negative reviews are loud enough to drag perception — the sample average sits at ${avg} stars, so pain themes deserve priority.`;
  if (mid > total * 0.3)
    return `Many two- and three-star reviews (${avg} stars on average) suggest interest without full satisfaction — fix expectation gaps.`;
  return `Ratings are spread across the scale (${avg} stars on average) — positioning clarity will matter for conversion.`;
}

export function storefrontMetric(
  storefronts: Record<string, number>,
  total: number
): string {
  const entries = Object.entries(storefronts).sort(([, a], [, b]) => b - a);
  if (!entries.length || total <= 0) return "";

  const [topCode, topCount] = entries[0];
  const { flag } = storefrontLabel(topCode);

  if (entries.length === 1) {
    return `${flag} Only market`;
  }

  const topPct = Math.round((topCount / total) * 100);
  if (topPct >= 45) {
    return `${topPct}% ${flag} ${topCode.toUpperCase()}`;
  }

  return `${entries.length} storefronts`;
}

export function storefrontInsight(storefronts: Record<string, number>) {
  const entries = Object.entries(storefronts).sort(([, a], [, b]) => b - a);
  if (entries.length <= 1) return "Most written reviews in this sample come from a single storefront.";
  const [top, second] = entries;
  if (top[1] > (second?.[1] ?? 0) * 3)
    return `${top[0].toUpperCase()} dominates the sample; international voices add pricing and trust themes.`;
  return "Multiple storefronts contribute — compare regional themes before global messaging changes.";
}
