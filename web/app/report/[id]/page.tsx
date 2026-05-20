import { ReportPolling } from "@/components/report-polling";

export default async function ReportPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <ReportPolling reportId={id} />;
}
