interface MetricCardProps {
  label: string;
  value: string | number;
  change?: string;
  trend?: "up" | "down" | "neutral";
}

export default function MetricCard({
  label,
  value,
  change,
  trend = "neutral",
}: MetricCardProps) {
  const trendColors = {
    up: "text-terminal-green",
    down: "text-terminal-red",
    neutral: "text-terminal-muted",
  };

  return (
    <div className="bg-terminal-surface border border-terminal-border rounded p-4">
      <div className="text-xs text-terminal-muted uppercase tracking-wider mb-1">
        {label}
      </div>
      <div className="text-2xl font-bold text-terminal-text">{value}</div>
      {change && (
        <div className={`text-xs mt-1 ${trendColors[trend]}`}>{change}</div>
      )}
    </div>
  );
}
