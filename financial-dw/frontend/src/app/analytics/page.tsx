"use client";

import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend,
  CartesianGrid,
} from "recharts";
import DataGrid from "@/components/data/DataGrid";
import MetricCard from "@/components/data/MetricCard";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import ErrorBanner from "@/components/common/ErrorBanner";
import {
  fetchTotals,
  fetchPredictions,
  fetchModelMetrics,
  runAggregation,
  runPrediction,
} from "@/lib/api";
import type { AggregateResult, PredictionResult, ModelMetrics } from "@/lib/types";

export default function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState<"aggregation" | "prediction">(
    "aggregation"
  );
  const [totals, setTotals] = useState<AggregateResult[]>([]);
  const [predictions, setPredictions] = useState<PredictionResult[]>([]);
  const [metrics, setMetrics] = useState<ModelMetrics[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [jobRunning, setJobRunning] = useState(false);

  useEffect(() => {
    loadResults();
  }, []);

  const loadResults = async () => {
    setLoading(true);
    setError(null);
    try {
      const [t, p, m] = await Promise.all([
        fetchTotals().catch(() => []),
        fetchPredictions().catch(() => []),
        fetchModelMetrics().catch(() => []),
      ]);
      setTotals(t as AggregateResult[]);
      setPredictions(p as PredictionResult[]);
      setMetrics(m as ModelMetrics[]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load results");
    } finally {
      setLoading(false);
    }
  };

  const handleRunAggregation = async () => {
    setJobRunning(true);
    try {
      await runAggregation("YFINANCE");
      await loadResults();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Aggregation job failed");
    } finally {
      setJobRunning(false);
    }
  };

  const handleRunPrediction = async () => {
    setJobRunning(true);
    try {
      await runPrediction("YFINANCE/BTC-USD", "YFINANCE");
      await loadResults();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Prediction job failed");
    } finally {
      setJobRunning(false);
    }
  };

  const aggColumns = [
    { key: "asset_id", label: "Asset ID", width: "50%" },
    { key: "business_date_year", label: "Year", width: "25%" },
    {
      key: "cnt",
      label: "Count",
      width: "25%",
      render: (val: number) => (val ?? 0).toLocaleString(),
    },
  ];

  const predColumns = [
    { key: "seconds", label: "Timestamp (s)", width: "33%" },
    {
      key: "open",
      label: "Actual",
      width: "33%",
      render: (val: number) => val?.toFixed(2) || "-",
    },
    {
      key: "prediction",
      label: "Predicted",
      width: "34%",
      render: (val: number) => val?.toFixed(2) || "-",
    },
  ];

  // Prepare chart data for aggregation (group by asset)
  const aggChartData = totals.map((t) => ({
    label: `${t.asset_id.split("/").pop()} (${t.business_date_year})`,
    count: t.cnt || 0,
    asset: t.asset_id.split("/").pop() || t.asset_id,
    year: t.business_date_year,
  }));

  // Prepare chart data for predictions
  const predChartData = predictions
    .slice()
    .sort((a, b) => a.seconds - b.seconds)
    .map((p) => ({
      seconds: p.seconds,
      actual: p.open,
      predicted: p.prediction,
    }));

  const tooltipStyle = {
    backgroundColor: "#161b22",
    border: "1px solid #30363d",
    borderRadius: "4px",
    color: "#e6edf3",
    fontSize: "11px",
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold text-terminal-green tracking-wider">
            ANALYTICS
          </h1>
          <p className="text-xs text-terminal-muted mt-1">
            Spark-powered aggregation and prediction results
          </p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard
          label="Aggregation Records"
          value={totals.length}
          trend="neutral"
        />
        <MetricCard
          label="Prediction Records"
          value={predictions.length}
          trend="neutral"
        />
        <MetricCard
          label="Total Data Points"
          value={totals.reduce((s, t) => s + (t.cnt || 0), 0).toLocaleString()}
          trend="up"
        />
      </div>

      {error && <ErrorBanner message={error} onRetry={loadResults} />}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-terminal-border pb-2">
        <button
          onClick={() => setActiveTab("aggregation")}
          className={`px-4 py-1.5 text-xs rounded-t border transition-colors ${
            activeTab === "aggregation"
              ? "border-terminal-cyan text-terminal-cyan bg-terminal-cyan/10 border-b-transparent"
              : "border-transparent text-terminal-muted hover:text-terminal-text"
          }`}
        >
          Aggregation Results
        </button>
        <button
          onClick={() => setActiveTab("prediction")}
          className={`px-4 py-1.5 text-xs rounded-t border transition-colors ${
            activeTab === "prediction"
              ? "border-terminal-cyan text-terminal-cyan bg-terminal-cyan/10 border-b-transparent"
              : "border-transparent text-terminal-muted hover:text-terminal-text"
          }`}
        >
          Prediction Results
        </button>
        <div className="flex-1" />
        {activeTab === "aggregation" ? (
          <button
            onClick={handleRunAggregation}
            disabled={jobRunning}
            className="px-3 py-1 text-xs bg-terminal-green/20 border border-terminal-green/50 text-terminal-green rounded hover:bg-terminal-green/30 transition-colors disabled:opacity-50"
          >
            {jobRunning ? "Running..." : "Run Aggregation"}
          </button>
        ) : (
          <button
            onClick={handleRunPrediction}
            disabled={jobRunning}
            className="px-3 py-1 text-xs bg-terminal-orange/20 border border-terminal-orange/50 text-terminal-orange rounded hover:bg-terminal-orange/30 transition-colors disabled:opacity-50"
          >
            {jobRunning ? "Running..." : "Run Prediction"}
          </button>
        )}
      </div>

      {/* Content */}
      {loading ? (
        <LoadingSpinner />
      ) : activeTab === "aggregation" ? (
        <div className="space-y-4">
          {/* Bar Chart */}
          {aggChartData.length > 0 && (
            <div className="bg-terminal-surface border border-terminal-border rounded p-4">
              <h3 className="text-xs text-terminal-muted uppercase tracking-wider mb-3">
                Record Count by Asset / Year
              </h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={aggChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                  <XAxis
                    dataKey="label"
                    tick={{ fill: "#8b949e", fontSize: 10 }}
                    stroke="#30363d"
                  />
                  <YAxis
                    tick={{ fill: "#8b949e", fontSize: 10 }}
                    stroke="#30363d"
                  />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Bar dataKey="count" fill="#00bcd4" radius={[2, 2, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
          {/* Data Table */}
          <div className="bg-terminal-surface border border-terminal-border rounded">
            <DataGrid
              columns={aggColumns}
              rows={totals}
              emptyMessage="No aggregation results yet. Run an aggregation job."
            />
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Line Chart -- Actual vs Predicted */}
          {predChartData.length > 0 && (
            <div className="bg-terminal-surface border border-terminal-border rounded p-4">
              <h3 className="text-xs text-terminal-muted uppercase tracking-wider mb-3">
                Actual vs Predicted
              </h3>
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={predChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                  <XAxis
                    dataKey="seconds"
                    tick={{ fill: "#8b949e", fontSize: 10 }}
                    stroke="#30363d"
                  />
                  <YAxis
                    tick={{ fill: "#8b949e", fontSize: 10 }}
                    stroke="#30363d"
                  />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Legend
                    wrapperStyle={{ fontSize: "11px", color: "#8b949e" }}
                  />
                  <Line
                    type="monotone"
                    dataKey="actual"
                    stroke="#00ff88"
                    dot={false}
                    strokeWidth={2}
                    name="Actual"
                  />
                  <Line
                    type="monotone"
                    dataKey="predicted"
                    stroke="#f0883e"
                    dot={false}
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    name="Predicted"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
          {/* Data Table */}
          <div className="bg-terminal-surface border border-terminal-border rounded">
            <DataGrid
              columns={predColumns}
              rows={predictions}
              emptyMessage="No prediction results yet. Run a prediction job."
            />
          </div>
          {/* Model Metrics */}
          {metrics.length > 0 && (
            <div className="bg-terminal-surface border border-terminal-border rounded p-4">
              <h3 className="text-xs text-terminal-muted uppercase tracking-wider mb-3">
                Model Evaluation Metrics
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {metrics.map((m, i) => (
                  <div
                    key={i}
                    className={`p-3 rounded border text-xs ${
                      m.is_best
                        ? "border-terminal-green/50 bg-terminal-green/5"
                        : "border-terminal-border bg-terminal-bg"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-terminal-cyan font-bold uppercase">
                        {m.model_name.replace("_", " ")}
                      </span>
                      {m.is_best && (
                        <span className="px-1.5 py-0.5 bg-terminal-green/20 text-terminal-green rounded text-[10px]">
                          BEST
                        </span>
                      )}
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-terminal-text">
                      <div>
                        <span className="text-terminal-muted">RMSE: </span>
                        {m.rmse.toFixed(4)}
                      </div>
                      <div>
                        <span className="text-terminal-muted">MAE: </span>
                        {m.mae.toFixed(4)}
                      </div>
                      <div>
                        <span className="text-terminal-muted">R²: </span>
                        {m.r2.toFixed(4)}
                      </div>
                    </div>
                    <div className="mt-1 text-terminal-muted">
                      {m.training_rows} rows, {m.feature_count} features
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
