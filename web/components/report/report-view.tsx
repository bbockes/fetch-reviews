import { ReportData } from "@/components/report/report-data";
import { ReportHero } from "@/components/report/report-hero";
import { ReportNav } from "@/components/report/report-nav";
import { ReportStats } from "@/components/report/report-stats";
import { ReportTakeaways } from "@/components/report/report-takeaways";
import { ReportThemes } from "@/components/report/report-themes";
import type { ReportResult } from "@/lib/types";

export function ReportView({ report }: { report: ReportResult }) {
  return (
    <article>
      <ReportHero summary={report.summary} />
      <ReportNav />

      <section id="overview" className="section-pad scroll-mt-28">
        <div className="container-apple">
          <h2 className="text-section-title text-center">At a glance.</h2>
          <p className="mx-auto mt-3 max-w-lg text-center text-[17px] text-subtle">
            The numbers behind this sample of App Store written reviews.
          </p>
          <div className="mt-12">
            <ReportStats report={report} />
          </div>
        </div>
      </section>

      <section id="data" className="section-muted section-pad scroll-mt-28">
        <div className="container-apple">
          <h2 className="text-section-title">By the numbers.</h2>
          <p className="mt-3 max-w-xl text-[17px] text-subtle">
            Rating breakdown and regional mix for this review sample.
          </p>
          <div className="mt-12">
            <ReportData report={report} />
          </div>
        </div>
      </section>

      <section id="themes" className="section-pad scroll-mt-28">
        <div className="container-apple">
          <h2 className="text-section-title text-center">In their words.</h2>
          <p className="mx-auto mt-3 max-w-lg text-center text-[17px] text-subtle">
            Ranked themes with real quotes from reviewers. Tap a theme to read more.
          </p>
          <div className="mt-12">
            <ReportThemes loves={report.loves} painPoints={report.pain_points} />
          </div>
        </div>
      </section>

      <section id="insights" className="section-muted section-pad scroll-mt-28">
        <div className="container-apple">
          <h2 className="text-section-title">What to do next.</h2>
          <p className="mt-3 max-w-xl text-[17px] text-subtle">
            Strategic takeaways distilled from recurring themes across reviews.
          </p>
          <div className="mt-10">
            <ReportTakeaways takeaways={report.takeaways} />
          </div>
        </div>
      </section>
    </article>
  );
}
