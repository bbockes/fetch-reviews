"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { createReport, parseApp } from "@/lib/api";

export function AnalyzeForm() {
  const router = useRouter();
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(demo = false) {
    setError(null);
    setLoading(true);
    try {
      if (demo) {
        router.push("/report/demo");
        return;
      }
      const appId = (await parseApp(input.trim())).app_id;
      const { report_id } = await createReport(appId);
      router.push(`/report/${report_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-stretch">
        <input
          type="url"
          placeholder="apps.apple.com/…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !loading && input.trim() && submit()}
          disabled={loading}
          className="min-h-[44px] flex-1 rounded-full border border-border bg-white px-5 text-[17px] text-foreground outline-none transition-shadow placeholder:text-subtle focus:border-[#0071e3] focus:ring-2 focus:ring-[#0071e3]/30"
        />
        <button
          type="button"
          disabled={loading || !input.trim()}
          onClick={() => submit(false)}
          className="min-h-[44px] shrink-0 rounded-full bg-[#0071e3] px-8 text-[17px] font-normal text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? "Starting…" : "Analyze"}
        </button>
      </div>

      {error && (
        <p className="text-center text-[14px] text-destructive" role="alert">
          {error}
        </p>
      )}

      <p className="text-center text-[14px] text-subtle">
        Or{" "}
        <button
          type="button"
          onClick={() => submit(true)}
          disabled={loading}
          className="link-apple disabled:opacity-50"
        >
          view the CookShelf sample report
        </button>
      </p>
    </div>
  );
}
