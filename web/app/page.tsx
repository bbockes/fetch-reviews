import { AnalyzeForm } from "@/components/analyze-form";

export default function HomePage() {
  return (
    <section className="section-pad text-center">
      <div className="container-apple mx-auto max-w-3xl">
        <h1 className="text-hero animate-hero-in text-balance">
          Discover what users
          <br className="hidden sm:block" /> are really saying.
        </h1>
        <p className="text-hero-sub animate-hero-in-delay mx-auto mt-10 max-w-2xl text-pretty">
          Paste an App Store link and get actionable insights from public reviews—organized
          by theme, ranked by importance, and grounded in real user quotes.
        </p>

        <div className="animate-hero-in-delay mx-auto mt-12 max-w-xl">
          <AnalyzeForm />
        </div>
      </div>
    </section>
  );
}
