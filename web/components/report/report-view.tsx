import { ReportData } from "@/components/report/report-data";
import { ReportHero } from "@/components/report/report-hero";
import { ReportHighlights } from "@/components/report/report-highlights";
import { ReportNav } from "@/components/report/report-nav";
import { ReportCard, ReportSectionLabel } from "@/components/report/report-section";
import { ReportTakeaways } from "@/components/report/report-takeaways";
import { ReportThemes } from "@/components/report/report-themes";
import { filterFeatureLoves, filterFeaturePains } from "@/lib/report-utils";
import type { ReportResult } from "@/lib/types";

export function ReportView({ report }: { report: ReportResult }) {
  const loves = filterFeatureLoves(report.loves);
  const painPoints = filterFeaturePains(report.pain_points);
  return (
    <article className="bg-white text-[17px] leading-relaxed">
      <ReportHero summary={report.summary} />
      <ReportNav />

      <div className="bg-secondary pb-16">
        <div className="mx-auto max-w-[1068px] space-y-12 px-6 py-10">
          <section id="highlights" className="scroll-mt-32">
            <ReportSectionLabel>Highlights</ReportSectionLabel>
            <ReportCard>
              <ReportHighlights report={report} />
            </ReportCard>
          </section>

          <section id="breakdown" className="scroll-mt-32">
            <ReportSectionLabel>Breakdown</ReportSectionLabel>
            <ReportData report={report} />
          </section>

          <section id="themes" className="scroll-mt-32">
            <ReportSectionLabel>What users love vs. what hurts</ReportSectionLabel>
            <ReportThemes loves={loves} painPoints={painPoints} />
          </section>

          <section id="takeaways" className="scroll-mt-32">
            <ReportSectionLabel>Strategic takeaways</ReportSectionLabel>
            <ReportTakeaways takeaways={report.takeaways} />
          </section>

          <p className="pt-2 text-center text-xs text-muted-foreground">
            Generated from public App Store written-review feeds. Not affiliated with Apple.
          </p>
        </div>
      </div>
    </article>
  );
}
