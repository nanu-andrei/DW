"use client";

interface SparklineCellProps {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
}

export default function SparklineCell({
  data,
  width = 80,
  height = 24,
  color = "#00ff88",
}: SparklineCellProps) {
  if (!data || data.length < 2) return <span className="text-terminal-muted">-</span>;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  const points = data
    .map((v, i) => {
      const x = (i / (data.length - 1)) * width;
      const y = height - ((v - min) / range) * height;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg width={width} height={height} className="inline-block">
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
      />
    </svg>
  );
}
