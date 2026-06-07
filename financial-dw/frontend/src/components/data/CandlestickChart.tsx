"use client";

import TimeSeriesChart from "./TimeSeriesChart";

interface CandlestickData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
}

interface CandlestickChartProps {
  data: CandlestickData[];
  height?: number;
}

export default function CandlestickChart({
  data,
  height = 400,
}: CandlestickChartProps) {
  return <TimeSeriesChart data={data} type="candlestick" height={height} />;
}
