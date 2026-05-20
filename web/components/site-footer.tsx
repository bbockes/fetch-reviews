export function SiteFooter() {
  return (
    <footer className="section-muted border-t border-border py-8">
      <div className="container-apple text-center text-[11px] leading-relaxed text-subtle">
        <p>
          Public written reviews only (~500 max per region). Not affiliated with Apple Inc.
        </p>
        <p className="mt-2 text-[10px] text-muted-foreground">
          Copyright © {new Date().getFullYear()} Review Intelligence. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
