"use client";

import { useQuery } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";

import { ReportView } from "@/components/report/report-view";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
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
      <div
        className="mx-auto space-y-8 px-6 py-16"
        style={{ maxWidth: "var(--max-content-width)" }}
      >
        <Skeleton className="h-16 w-2/3 rounded-2xl" />
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-28 rounded-3xl" />
          ))}
        </div>
        <Skeleton className="h-56 rounded-3xl" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-lg px-6 py-32 text-center">
        <p className="text-sm text-[#707070]">{error.message}</p>
      </div>
    );
  }

  if (!data) return null;

  if (data.status === "failed") {
    return (
      <div className="mx-auto max-w-lg px-6 py-32 text-center">
        <p className="text-lg font-semibold tracking-[-0.02em] text-foreground">Report failed</p>
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{data.error}</p>
      </div>
    );
  }

  if (data.status !== "complete" || !data.result) {
    const progress =
      data.status === "queued" ? 10 : data.status === "fetching" ? 45 : 75;

    return (
      <div className="mx-auto flex max-w-lg flex-col items-center px-6 py-40 text-center">
        <Loader2 className="mb-8 size-9 animate-spin text-brand" strokeWidth={1.5} />
        <h1 className="text-2xl font-semibold tracking-[-0.03em] text-foreground">
          Building your report
        </h1>
        <p className="mt-3 text-sm text-muted-foreground">
          {data.progress_message ?? "Working…"}
        </p>
        <Progress value={progress} className="mt-10 h-1.5 w-full max-w-sm" />
        <p className="mt-5 text-xs text-muted-foreground">
          Fetching public written reviews can take up to a minute.
        </p>
      </div>
    );
  }

  return <ReportView report={data.result} />;
}
