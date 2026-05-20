"use client";

import { useQuery } from "@tanstack/react-query";

import { ReportView } from "@/components/report/report-view";
import { getReport } from "@/lib/api";

export function ReportPolling({ reportId }: { reportId: string }) {
  const isDemo = reportId === "demo";

  const { data, error, isLoading } = useQuery({
    queryKey: ["report", reportId],
    queryFn: () => getReport(reportId),
    refetchInterval: (query) => {
      if (isDemo) return false;
      const status = query.state.data?.status;
      if (status === "complete" || status === "failed") return false;
      return 1500;
    },
  });

  if (isLoading && !data) {
    return (
      <div className="section-pad text-center">
        <div className="container-apple mx-auto max-w-md animate-pulse space-y-4">
          <div className="mx-auto h-4 w-24 rounded bg-border/60" />
          <div className="mx-auto h-12 w-2/3 rounded-lg bg-border/60" />
          <div className="mx-auto h-5 w-full rounded bg-border/40" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="section-pad text-center">
        <div className="container-apple max-w-md">
          <p className="text-[17px] text-subtle">{error.message}</p>
          <p className="mt-4">
            <a href="/" className="link-apple text-[14px]">
              Start over
            </a>
          </p>
        </div>
      </div>
    );
  }

  if (!data) return null;

  if (data.status === "failed") {
    return (
      <div className="section-pad text-center">
        <div className="container-apple max-w-md">
          <h1 className="text-section-title">Something went wrong.</h1>
          <p className="mt-4 text-[17px] text-subtle">{data.error}</p>
          <p className="mt-6">
            <a href="/" className="link-apple text-[14px]">
              Try another app
            </a>
          </p>
        </div>
      </div>
    );
  }

  if (data.status !== "complete" || !data.result) {
    const progress =
      data.status === "queued" ? 10 : data.status === "fetching" ? 45 : 75;

    return (
      <div className="section-pad text-center">
        <div className="container-apple mx-auto max-w-md">
          <h1 className="text-section-title">Building your report.</h1>
          <p className="mt-4 text-[17px] text-subtle">
            {data.progress_message ?? "Reading public written reviews…"}
          </p>
          <div className="mx-auto mt-10 h-1 max-w-xs overflow-hidden rounded-full bg-border">
            <div
              className="h-full rounded-full bg-[#0071e3] transition-all duration-700 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="mt-6 text-[12px] text-subtle">
            This usually takes less than a minute.
          </p>
        </div>
      </div>
    );
  }

  return <ReportView report={data.result} />;
}
