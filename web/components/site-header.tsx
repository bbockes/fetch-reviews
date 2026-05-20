import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 border-b border-border/80 bg-white/80 backdrop-blur-xl backdrop-saturate-150">
      <div
        className="mx-auto flex items-center justify-between px-6"
        style={{ height: "var(--navbar-height)", maxWidth: "var(--max-content-width)" }}
      >
        <Link
          href="/"
          className="text-[15px] font-semibold tracking-[-0.02em] text-foreground transition-opacity hover:opacity-70"
        >
          Review Intelligence
        </Link>
        <Link
          href="/"
          className="rounded-full bg-secondary px-5 py-2 text-sm font-medium text-foreground transition-colors hover:bg-[#e0e0e0]"
        >
          New report
        </Link>
      </div>
    </header>
  );
}
