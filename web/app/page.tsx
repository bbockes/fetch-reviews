import { AnalyzeForm } from "@/components/analyze-form";

export default function HomePage() {
  return (
    <section className="section-pad text-center">
      <div className="container-apple mx-auto max-w-3xl">
        <h1 className="text-hero animate-hero-in text-balance">
          Understand what users
          <br className="hidden sm:block" /> are really saying.
        </h1>
        <p className="text-hero-sub animate-hero-in-delay mx-auto mt-5 max-w-xl text-pretty">
          Paste an App Store link. We read public written reviews and return ranked
          themes with the quotes behind them.
        </p>

        <div className="animate-hero-in-delay mx-auto mt-12 max-w-lg">
          <AnalyzeForm />
        </div>
      </div>
    </section>
  );
}
