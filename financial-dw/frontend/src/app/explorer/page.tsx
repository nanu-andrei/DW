"use client";

import { useState, useEffect } from "react";
import SplitPane from "@/components/layout/SplitPane";
import TimeSeriesChart from "@/components/data/TimeSeriesChart";
import DataGrid from "@/components/data/DataGrid";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import ErrorBanner from "@/components/common/ErrorBanner";
import { fetchAssets, fetchDataSources, fetchTimeSeries } from "@/lib/api";
import type {
  TimeSeriesResponse,
  TimeSeriesRecord,
  PaginatedResponse,
} from "@/lib/types";

export default function ExplorerPage() {
  const [assetIds, setAssetIds] = useState<string[]>([]);
  const [dataSourceIds, setDataSourceIds] = useState<string[]>([]);
  const [assetId, setAssetId] = useState("");
  const [dataSourceId, setDataSourceId] = useState("");
  const [startDate, setStartDate] = useState("2023-01-01");
  const [endDate, setEndDate] = useState("2023-12-31");
  const [chartType, setChartType] = useState<"line" | "candlestick">("line");
  const [data, setData] = useState<TimeSeriesResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingSelectors, setLoadingSelectors] = useState(true);

  // Load available assets and data sources for dropdowns
  useEffect(() => {
    const loadSelectors = async () => {
      try {
        const [assetsRes, dsRes] = await Promise.all([
          fetchAssets(0, 100).catch(() => ({ items: [] })),
          fetchDataSources(0, 100).catch(() => ({ items: [] })),
        ]);
        const assets = (assetsRes as PaginatedResponse).items || [];
        const sources = (dsRes as PaginatedResponse).items || [];
        setAssetIds(assets);
        setDataSourceIds(sources);
        if (assets.length > 0) setAssetId(assets[0]);
        if (sources.length > 0) setDataSourceId(sources[0]);
      } catch {
        // silently fail -- user can still type manually
      } finally {
        setLoadingSelectors(false);
      }
    };
    loadSelectors();
  }, []);

  const handleSearch = async () => {
    if (!assetId || !dataSourceId) {
      setError("Asset ID and Data Source ID are required");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = (await fetchTimeSeries(
        assetId,
        dataSourceId,
        startDate,
        endDate,
        true
      )) as TimeSeriesResponse;
      setData(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to fetch data");
    } finally {
      setLoading(false);
    }
  };

  const chartData =
    data?.data.records
      .slice()
      .reverse()
      .map((r: TimeSeriesRecord) => ({
        time: r.businessDate,
        open: (r.values.Open as number) || (r.values.Mid as number) || 0,
        high: (r.values.High as number) || (r.values.Mid as number) || 0,
        low: (r.values.Low as number) || (r.values.Mid as number) || 0,
        close: (r.values.Close as number) || (r.values.Last as number) || 0,
        value: (r.values.Close as number) || (r.values.Mid as number) || 0,
      })) || [];

  const gridColumns = [
    { key: "businessDate", label: "Date", width: "20%" },
    ...Object.keys(data?.data.records[0]?.values || {}).map((key) => ({
      key,
      label: key,
      render: (val: any) =>
        typeof val === "number"
          ? val.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })
          : val ?? "-",
    })),
  ];

  const gridRows =
    data?.data.records.map((r: TimeSeriesRecord) => ({
      businessDate: r.businessDate,
      ...r.values,
    })) || [];

  const leftPanel = (
    <div className="p-4 space-y-4">
      <h2 className="text-sm font-bold text-terminal-green uppercase tracking-wider">
        Query Parameters
      </h2>

      <div className="space-y-3">
        <div>
          <label className="text-xs text-terminal-muted block mb-1">
            Asset ID
          </label>
          {loadingSelectors ? (
            <div className="text-xs text-terminal-muted py-2">Loading...</div>
          ) : assetIds.length > 0 ? (
            <select
              value={assetId}
              onChange={(e) => setAssetId(e.target.value)}
              className="w-full bg-terminal-bg border border-terminal-border rounded px-3 py-2 text-xs text-terminal-text focus:border-terminal-cyan outline-none"
            >
              <option value="">Select an asset...</option>
              {assetIds.map((id) => (
                <option key={id} value={id}>
                  {id}
                </option>
              ))}
            </select>
          ) : (
            <input
              type="text"
              value={assetId}
              onChange={(e) => setAssetId(e.target.value)}
              placeholder="e.g. YFINANCE/BTC-USD"
              className="w-full bg-terminal-bg border border-terminal-border rounded px-3 py-2 text-xs text-terminal-text placeholder:text-terminal-muted/50 focus:border-terminal-cyan outline-none"
            />
          )}
        </div>

        <div>
          <label className="text-xs text-terminal-muted block mb-1">
            Data Source ID
          </label>
          {loadingSelectors ? (
            <div className="text-xs text-terminal-muted py-2">Loading...</div>
          ) : dataSourceIds.length > 0 ? (
            <select
              value={dataSourceId}
              onChange={(e) => setDataSourceId(e.target.value)}
              className="w-full bg-terminal-bg border border-terminal-border rounded px-3 py-2 text-xs text-terminal-text focus:border-terminal-cyan outline-none"
            >
              <option value="">Select a data source...</option>
              {dataSourceIds.map((id) => (
                <option key={id} value={id}>
                  {id}
                </option>
              ))}
            </select>
          ) : (
            <input
              type="text"
              value={dataSourceId}
              onChange={(e) => setDataSourceId(e.target.value)}
              placeholder="e.g. YFINANCE"
              className="w-full bg-terminal-bg border border-terminal-border rounded px-3 py-2 text-xs text-terminal-text placeholder:text-terminal-muted/50 focus:border-terminal-cyan outline-none"
            />
          )}
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="text-xs text-terminal-muted block mb-1">
              Start Date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full bg-terminal-bg border border-terminal-border rounded px-3 py-2 text-xs text-terminal-text focus:border-terminal-cyan outline-none"
            />
          </div>
          <div>
            <label className="text-xs text-terminal-muted block mb-1">
              End Date
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full bg-terminal-bg border border-terminal-border rounded px-3 py-2 text-xs text-terminal-text focus:border-terminal-cyan outline-none"
            />
          </div>
        </div>

        <div>
          <label className="text-xs text-terminal-muted block mb-1">
            Chart Type
          </label>
          <div className="flex gap-2">
            <button
              onClick={() => setChartType("line")}
              className={`px-3 py-1 text-xs rounded border transition-colors ${
                chartType === "line"
                  ? "border-terminal-cyan text-terminal-cyan bg-terminal-cyan/10"
                  : "border-terminal-border text-terminal-muted hover:border-terminal-cyan"
              }`}
            >
              Line
            </button>
            <button
              onClick={() => setChartType("candlestick")}
              className={`px-3 py-1 text-xs rounded border transition-colors ${
                chartType === "candlestick"
                  ? "border-terminal-cyan text-terminal-cyan bg-terminal-cyan/10"
                  : "border-terminal-border text-terminal-muted hover:border-terminal-cyan"
              }`}
            >
              Candlestick
            </button>
          </div>
        </div>

        <button
          onClick={handleSearch}
          disabled={loading}
          className="w-full py-2 bg-terminal-green/20 border border-terminal-green/50 text-terminal-green text-xs rounded hover:bg-terminal-green/30 transition-colors disabled:opacity-50"
        >
          {loading ? "Loading..." : "FETCH DATA"}
        </button>
      </div>

      {data?.attributes && (
        <div>
          <h3 className="text-xs text-terminal-muted uppercase tracking-wider mb-2">
            Available Attributes
          </h3>
          <div className="flex flex-wrap gap-1">
            {data.attributes.map((attr) => (
              <span
                key={attr}
                className="text-[10px] bg-terminal-bg px-1.5 py-0.5 rounded border border-terminal-border text-terminal-cyan"
              >
                {attr}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const rightPanel = (
    <div className="p-4 space-y-4">
      {error && <ErrorBanner message={error} />}

      {loading && <LoadingSpinner />}

      {!loading && data && (
        <>
          <div className="flex items-center justify-between">
            <span className="text-xs text-terminal-muted">
              {data.data.records.length} records
            </span>
            <span className="text-xs text-terminal-cyan">
              {data.data.assetId}
            </span>
          </div>
          <TimeSeriesChart data={chartData} type={chartType} height={350} />
          <div className="bg-terminal-surface border border-terminal-border rounded">
            <DataGrid columns={gridColumns} rows={gridRows} />
          </div>
        </>
      )}

      {!loading && !data && !error && (
        <div className="flex items-center justify-center h-64 text-terminal-muted text-sm">
          Configure parameters and click FETCH DATA to explore time series
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-lg font-bold text-terminal-green tracking-wider">
          EXPLORER
        </h1>
        <p className="text-xs text-terminal-muted mt-1">
          Browse and visualize time series data
        </p>
      </div>

      <div
        className="bg-terminal-surface border border-terminal-border rounded"
        style={{ height: "calc(100vh - 140px)" }}
      >
        <SplitPane left={leftPanel} right={rightPanel} />
      </div>
    </div>
  );
}
