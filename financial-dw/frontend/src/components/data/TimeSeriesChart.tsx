"use client";

import { useEffect, useRef } from "react";

interface DataPoint {
  time: string;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  value?: number;
}

interface TimeSeriesChartProps {
  data: DataPoint[];
  type?: "candlestick" | "line";
  height?: number;
}

export default function TimeSeriesChart({
  data,
  type = "line",
  height = 400,
}: TimeSeriesChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const resizeHandlerRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    if (!containerRef.current || data.length === 0) return;

    let cancelled = false;

    const initChart = async () => {
      try {
        const { createChart, ColorType, LineStyle } = await import(
          "lightweight-charts"
        );

        if (cancelled || !containerRef.current) return;

        // Clean up previous chart
        if (chartRef.current) {
          chartRef.current.remove();
          chartRef.current = null;
        }
        if (resizeHandlerRef.current) {
          window.removeEventListener("resize", resizeHandlerRef.current);
          resizeHandlerRef.current = null;
        }

        containerRef.current.innerHTML = "";

        const chart = createChart(containerRef.current, {
          width: containerRef.current.clientWidth,
          height,
          layout: {
            background: { type: ColorType.Solid, color: "#0d1117" },
            textColor: "#8b949e",
            fontFamily: "JetBrains Mono, monospace",
            fontSize: 10,
          },
          grid: {
            vertLines: { color: "#21262d" },
            horzLines: { color: "#21262d" },
          },
          crosshair: {
            vertLine: { color: "#30363d", style: LineStyle.Dashed },
            horzLine: { color: "#30363d", style: LineStyle.Dashed },
          },
          timeScale: {
            borderColor: "#30363d",
            timeVisible: false,
          },
          rightPriceScale: { borderColor: "#30363d" },
        });

        chartRef.current = chart;

        if (type === "candlestick") {
          const series = chart.addCandlestickSeries({
            upColor: "#00ff88",
            downColor: "#ff4444",
            borderUpColor: "#00ff88",
            borderDownColor: "#ff4444",
            wickUpColor: "#00ff88",
            wickDownColor: "#ff4444",
          });
          series.setData(data);
        } else {
          const series = chart.addLineSeries({
            color: "#00bcd4",
            lineWidth: 2,
          });
          series.setData(
            data.map((d) => ({
              time: d.time,
              value: d.value ?? d.close ?? 0,
            }))
          );
        }

        chart.timeScale().fitContent();

        const handleResize = () => {
          if (containerRef.current && chartRef.current) {
            chartRef.current.applyOptions({
              width: containerRef.current.clientWidth,
            });
          }
        };

        resizeHandlerRef.current = handleResize;
        window.addEventListener("resize", handleResize);
      } catch (e) {
        console.error("Failed to load chart library:", e);
      }
    };

    initChart();

    return () => {
      cancelled = true;
      if (resizeHandlerRef.current) {
        window.removeEventListener("resize", resizeHandlerRef.current);
        resizeHandlerRef.current = null;
      }
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [data, type, height]);

  if (data.length === 0) {
    return (
      <div
        className="flex items-center justify-center bg-terminal-bg border border-terminal-border rounded text-terminal-muted text-sm"
        style={{ height }}
      >
        No data to display
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="bg-terminal-bg border border-terminal-border rounded"
      style={{ height }}
    />
  );
}
