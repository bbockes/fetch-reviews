"use client";

import { Check, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

import { cn } from "@/lib/utils";

const STEPS = [
  { id: "fetch", label: "Fetching reviews" },
  { id: "classify", label: "Classifying sentiment" },
  { id: "extract", label: "Extracting quotes" },
] as const;

function activeStepIndex(status: string, message: string): number {
  if (status === "queued" || status === "fetching") return 0;
  if (status !== "analyzing") return 0;
  if (message.toLowerCase().includes("extracting")) return 2;
  if (message.toLowerCase().includes("classifying")) return 1;
  return 1;
}

function formatElapsed(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
}

export function ReportProcessing({
  status,
  progressMessage,
}: {
  status: string;
  progressMessage?: string | null;
}) {
  const message = progressMessage ?? "Reading public written reviews…";
  const active = activeStepIndex(status, message);
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const started = Date.now();
    const timer = window.setInterval(() => {
      setElapsed(Math.floor((Date.now() - started) / 1000));
    }, 1000);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <div className="section-pad text-center">
      <div className="container-apple mx-auto max-w-md">
        <h1 className="text-section-title">Building your report.</h1>
        <p className="mt-4 text-[17px] text-subtle">{message}</p>

        <ol className="mx-auto mt-10 max-w-sm space-y-3 text-left">
          {STEPS.map((step, index) => {
            const done = index < active;
            const current = index === active;
            return (
              <li
                key={step.id}
                className={cn(
                  "flex items-center gap-3 rounded-xl border px-4 py-3 transition-colors",
                  current && "border-[#0071e3]/30 bg-[#0071e3]/5",
                  done && "border-border/60 bg-white",
                  !done && !current && "border-border/40 bg-secondary/30 opacity-60"
                )}
              >
                <span
                  className={cn(
                    "flex size-7 shrink-0 items-center justify-center rounded-full",
                    done && "bg-emerald-500 text-white",
                    current && "bg-[#0071e3] text-white",
                    !done && !current && "bg-border/60 text-muted-foreground"
                  )}
                >
                  {done ? (
                    <Check className="size-3.5" strokeWidth={3} />
                  ) : current ? (
                    <Loader2 className="size-3.5 animate-spin" />
                  ) : (
                    <span className="text-xs font-medium">{index + 1}</span>
                  )}
                </span>
                <span
                  className={cn(
                    "text-[15px]",
                    current ? "font-medium text-foreground" : "text-muted-foreground"
                  )}
                >
                  {step.label}
                </span>
              </li>
            );
          })}
        </ol>

        <div className="relative mx-auto mt-8 h-1.5 max-w-xs overflow-hidden rounded-full bg-border">
          <div className="absolute inset-y-0 w-1/3 animate-[report-load_1.4s_ease-in-out_infinite] rounded-full bg-[#0071e3]" />
        </div>

        <p className="mt-6 text-[13px] text-subtle">
          AI analysis usually takes 1–2 minutes · {formatElapsed(elapsed)} elapsed
        </p>
      </div>
    </div>
  );
}
