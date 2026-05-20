/** Section label — sits above content blocks, never inside the white card */
export function ReportSectionLabel({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <h2
      className={`mb-4 text-lg font-semibold tracking-tight text-foreground sm:text-xl ${className}`}
    >
      {children}
    </h2>
  );
}

export function ReportCard({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`rounded-2xl border border-border/70 bg-white p-6 shadow-sm sm:p-8 ${className}`}
    >
      {children}
    </div>
  );
}
