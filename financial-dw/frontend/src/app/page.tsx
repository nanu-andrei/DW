"use client";

import { useEffect, useState } from "react";
import MetricCard from "@/components/data/MetricCard";
import { fetchAssets, fetchDataSources, fetchTotals } from "@/lib/api";
import type { PaginatedResponse, AggregateResult } from "@/lib/types";

export default function DashboardPage() {
  const [metrics, setMetrics] = useState({
    totalAssets: 0,
    totalDataSources: 0,
    totalRecords: 0,
    lastIngestion: "-",
  });
  const [loading, setLoading] = useState(true);
  const [logs] = useState([
    { time: "12:00:01", msg: "System initialized" },
    { time: "12:00:02", msg: "Connected to Cassandra cluster" },
    { time: "12:00:03", msg: "API endpoints registered" },
    { time: "12:00:04", msg: "Ready to accept connections" },
  ]);

  useEffect(() => {
    const loadMetrics = async () => {
      try {
        const [assetsRes, dsRes] = await Promise.all([
          fetchAssets(0, 1).catch(() => ({ total: 0 })),
          fetchDataSources(0, 1).catch(() => ({ total: 0 })),
        ]);

        let totalRecords = 0;
        try {
          const totals = (await fetchTotals()) as AggregateResult[];
          totalRecords = totals.reduce(
            (sum: number, t: AggregateResult) => sum + t.cnt,
            0
          );
        } catch {
          totalRecords = 0;
        }

        setMetrics({
          totalAssets: (assetsRes as PaginatedResponse).total || 0,
          totalDataSources: (dsRes as PaginatedResponse).total || 0,
          totalRecords,
          lastIngestion: new Date().toISOString().split("T")[0],
        });
      } catch (error) {
        console.error("Failed to load metrics:", error);
      } finally {
        setLoading(false);
      }
    };

    loadMetrics();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-lg font-bold text-terminal-green tracking-wider">
          DASHBOARD
        </h1>
        <p className="text-xs text-terminal-muted mt-1">
          Acme Ltd Financial Data Warehouse Overview
        </p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Total Assets"
          value={loading ? "..." : metrics.totalAssets}
          trend="neutral"
        />
        <MetricCard
          label="Data Sources"
          value={loading ? "..." : metrics.totalDataSources}
          trend="neutral"
        />
        <MetricCard
          label="Total Records"
          value={loading ? "..." : metrics.totalRecords.toLocaleString()}
          trend="up"
          change="+0 today"
        />
        <MetricCard
          label="Last Ingestion"
          value={loading ? "..." : metrics.lastIngestion}
          trend="neutral"
        />
      </div>

      {/* Activity Log */}
      <div className="bg-terminal-surface border border-terminal-border rounded">
        <div className="px-4 py-2 border-b border-terminal-border">
          <span className="text-xs text-terminal-muted uppercase tracking-wider">
            System Activity Log
          </span>
        </div>
        <div className="p-4 space-y-1 font-mono text-xs max-h-64 overflow-auto">
          {logs.map((log, i) => (
            <div key={i} className="flex gap-3">
              <span className="text-terminal-muted">[{log.time}]</span>
              <span className="text-terminal-text">{log.msg}</span>
            </div>
          ))}
          <div className="flex gap-3 text-terminal-green">
            <span className="text-terminal-muted">
              [{new Date().toLocaleTimeString("en-US", { hour12: false })}]
            </span>
            <span>System ready</span>
            <span className="cursor-blink">_</span>
          </div>
        </div>
      </div>
    </div>
  );
}
