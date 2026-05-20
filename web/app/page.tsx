import { AnalyzeForm } from "@/components/analyze-form";

export default function HomePage() {
  return (
    <div className="relative flex flex-1 flex-col items-center overflow-hidden px-6 pb-24 pt-16 sm:pb-32 sm:pt-24">
      <div
        className="pointer-events-none absolute inset-x-0 top-0 h-[480px] opacity-60"
        aria-hidden
        style={{
          background:
            "radial-gradient(ellipse 80% 50% at 50% -20%, rgba(237, 237, 237, 0.9), transparent)",
        }}
      />

      <div className="relative z-10 w-full max-w-3xl space-y-12 text-center sm:space-y-16">
        <div className="space-y-6 animate-fade-in-up">
          <p className="text-label text-brand">App Store review intelligence</p>
          <h1 className="text-display mx-auto max-w-4xl text-balance">
            What are users really saying?
          </h1>
          <p className="text-body-lg mx-auto max-w-xl text-pretty">
            Paste any iOS app&apos;s App Store link. We fetch public written reviews and
            surface ranked themes with real quotes.
          </p>
        </div>

        <div className="animate-fade-in-up-delay-1">
          <AnalyzeForm />
        </div>

        <div className="animate-fade-in-up-delay-2">
          <p className="mx-auto max-w-md text-sm leading-relaxed text-muted-foreground">
            Public written reviews only (~500 max per region). Not affiliated with Apple.
          </p>
        </div>
      </div>
    </div>
  );
}
