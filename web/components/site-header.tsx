import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-white">
      <div
        className="container-apple-wide flex items-center justify-between"
        style={{ height: "var(--nav-height)" }}
      >
        <Link
          href="/"
          className="text-[12px] font-normal text-foreground/80 transition-opacity hover:text-foreground"
        >
          Fetch
        </Link>
        <nav className="flex items-center gap-6 text-[12px]">
          <Link
            href="/"
            className="text-foreground/80 transition-opacity hover:text-foreground"
          >
            Analyze
          </Link>
          <Link href="/report/demo" className="link-apple">
            Sample report
          </Link>
        </nav>
      </div>
    </header>
  );
}
