export type Quote = {
  author: string;
  storefront: string;
  rating: number | null;
  excerpt: string;
};

export type Theme = {
  mention_count: number;
  title: string;
  quotes: Quote[];
  also_noted?: string | null;
};

export type ReportSummary = {
  average_rating: number;
  total_reviews: number;
  one_liner: string;
  app_id: string;
  app_name?: string | null;
  app_url?: string | null;
  rating_distribution: Record<string, number>;
  storefronts: Record<string, number>;
  generated_at: string;
};

export type ReportResult = {
  summary: ReportSummary;
  loves: Theme[];
  pain_points: Theme[];
  takeaways: string[];
};

export type ReportJob = {
  id: string;
  status: "queued" | "fetching" | "analyzing" | "complete" | "failed";
  progress_message?: string | null;
  error?: string | null;
  result?: ReportResult | null;
};
