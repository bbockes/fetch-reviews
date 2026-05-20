"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
    <div className="mx-auto w-full max-w-xl space-y-6">
      <div className="shadow-elevated rounded-[28px] border border-border/60 bg-white p-2 sm:p-3">
        <Input
          placeholder="App Store URL or ID — apps.apple.com/.../id123456789"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !loading && input.trim() && submit()}
          disabled={loading}
          className="h-14 border-0 bg-transparent px-5 text-base shadow-none focus-visible:ring-0"
        />
        <Button
          className="mt-2 h-12 w-full rounded-[20px] bg-foreground text-[15px] font-medium text-background transition-all hover:bg-foreground/90 active:scale-[0.99]"
          disabled={loading || !input.trim()}
          onClick={() => submit(false)}
        >
          {loading ? "Starting…" : "Analyze reviews"}
        </Button>
      </div>

      {error && (
        <p className="text-center text-sm text-[#707070]" role="alert">
          {error}
        </p>
      )}

      <button
        type="button"
        onClick={() => submit(true)}
        disabled={loading}
        className="w-full text-center text-[15px] font-medium text-brand transition-colors hover:text-foreground disabled:opacity-50"
      >
        Try the CookShelf sample report
      </button>
    </div>
  );
}
