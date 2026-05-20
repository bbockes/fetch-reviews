"use client";

import { useEffect, useState } from "react";

import { cn } from "@/lib/utils";

const SECTIONS = [
  { id: "overview", label: "Overview" },
  { id: "data", label: "Numbers" },
  { id: "themes", label: "Themes" },
  { id: "insights", label: "Next steps" },
] as const;

export function ReportNav() {
  const [active, setActive] = useState<string>("overview");

  useEffect(() => {
    const ids = SECTIONS.map((s) => s.id);
    const elements = ids
      .map((id) => document.getElementById(id))
      .filter((el): el is HTMLElement => el != null);

    if (!elements.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (visible[0]?.target.id) setActive(visible[0].target.id);
      },
      { rootMargin: "-40% 0px -50% 0px", threshold: [0, 0.25, 0.5] }
    );

    elements.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  return (
    <nav
      className="sticky z-40 border-b border-border bg-[rgba(255,255,255,0.8)] backdrop-blur-xl backdrop-saturate-[180%]"
      style={{ top: "var(--nav-height)" }}
      aria-label="Report sections"
    >
      <div className="container-apple flex justify-center gap-1 overflow-x-auto py-2 sm:gap-2">
        {SECTIONS.map(({ id, label }) => (
          <a
            key={id}
            href={`#${id}`}
            onClick={() => setActive(id)}
            className={cn(
              "shrink-0 rounded-full px-4 py-1.5 text-[12px] transition-colors",
              active === id
                ? "bg-foreground text-background"
                : "text-subtle hover:text-foreground"
            )}
          >
            {label}
          </a>
        ))}
      </div>
    </nav>
  );
}
