import type { LucideIcon } from "lucide-react";
import {
  AlertCircle,
  AlertTriangle,
  Heart,
  Lightbulb,
  LineChart,
  ScanEye,
  Star,
  Target,
  TrendingDown,
  TrendingUp,
} from "lucide-react";

import type { ReportTone } from "@/lib/report-utils";
import { cn } from "@/lib/utils";

const ICON_STROKE = 1.5;

/** Matches love / pain tabs in themes — insight is neutral strategic */
export const TONE_STYLES: Record<
  ReportTone,
  { container: string; icon: string }
> = {
  love: {
    container: "border-emerald-200/70 bg-emerald-50",
    icon: "text-emerald-800",
  },
  pain: {
    container: "border-red-200/70 bg-red-50",
    icon: "text-red-800",
  },
  insight: {
    container: "border-sky-200/70 bg-sky-50",
    icon: "text-sky-800",
  },
};

export function ReportIcon({
  icon: Icon,
  tone,
  size = "md",
  className,
}: {
  icon: LucideIcon;
  tone: ReportTone;
  size?: "md" | "lg";
  className?: string;
}) {
  const styles = TONE_STYLES[tone];

  return (
    <div
      className={cn(
        "flex shrink-0 items-center justify-center rounded-[14px] border shadow-[0_1px_2px_rgba(0,0,0,0.03)]",
        styles.container,
        size === "lg" ? "size-14" : "size-12",
        className
      )}
    >
      <Icon
        className={cn(styles.icon, size === "lg" ? "size-[22px]" : "size-5")}
        strokeWidth={ICON_STROKE}
        aria-hidden
      />
    </div>
  );
}

export const HIGHLIGHT_ITEMS = [
  { icon: Star, tone: "love" as const },
  { icon: TrendingDown, tone: "pain" as const },
  { icon: Heart, tone: "love" as const },
  { icon: AlertCircle, tone: "pain" as const },
];

export const TAKEAWAY_ICON_BY_TONE: Record<
  ReportTone,
  LucideIcon[]
> = {
  love: [TrendingUp, Heart, Target],
  pain: [AlertTriangle, TrendingDown, AlertCircle],
  insight: [Lightbulb, ScanEye, LineChart],
};

export function takeawayIcon(tone: ReportTone, index: number): LucideIcon {
  const icons = TAKEAWAY_ICON_BY_TONE[tone];
  return icons[index % icons.length];
}

export { ICON_STROKE };
