"use client";

import { useEffect, useState } from "react";

import { cn } from "@/lib/utils";

const SECTIONS = [
  { id: "highlights", label: "Highlights" },
  { id: "breakdown", label: "Breakdown" },
  { id: "themes", label: "Themes" },
  { id: "takeaways", label: "Takeaways" },
] as const;

export function ReportNav() {
  const [active, setActive] = useState<string>("highlights");

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
      { rootMargin: "-35% 0px -55% 0px", threshold: [0, 0.2, 0.4] }
    );

    elements.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  return (
    <nav
      className="sticky z-40 border-b border-border bg-white/95 backdrop-blur-md"
      style={{ top: "var(--nav-height)" }}
      aria-label="Report sections"
    >
      <div className="mx-auto flex max-w-[1068px] gap-6 overflow-x-auto px-6">
        {SECTIONS.map(({ id, label }) => (
          <a
            key={id}
            href={`#${id}`}
            onClick={() => setActive(id)}
            className={cn(
              "shrink-0 border-b-2 py-3.5 text-base font-medium transition-colors sm:text-[17px]",
              active === id
                ? "border-foreground text-foreground"
                : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            {label}
          </a>
        ))}
      </div>
    </nav>
  );
}
