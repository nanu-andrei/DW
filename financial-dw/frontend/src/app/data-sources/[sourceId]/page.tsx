"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import ErrorBanner from "@/components/common/ErrorBanner";
import { fetchDataSourceDetails } from "@/lib/api";
import type { DataSource } from "@/lib/types";

export default function DataSourceDetailPage() {
  const params = useParams();
  const sourceId = decodeURIComponent(params.sourceId as string);
  const [versions, setVersions] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDetails = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = (await fetchDataSourceDetails(sourceId)) as DataSource[];
      setVersions(data);
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Failed to load data source"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDetails();
  }, [sourceId]);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorBanner message={error} onRetry={loadDetails} />;

  const latest = versions[0];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-bold text-terminal-green tracking-wider">
          DATA SOURCE DETAIL
        </h1>
        <p className="text-sm text-terminal-cyan mt-1">{sourceId}</p>
      </div>

      {latest && (
        <div className="bg-terminal-surface border border-terminal-green/30 rounded p-4">
          <div className="text-xs text-terminal-green uppercase tracking-wider mb-3">
            Latest Version
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-terminal-muted">Name:</span>{" "}
              <span className="text-terminal-text">{latest.name}</span>
            </div>
            <div>
              <span className="text-terminal-muted">Updated:</span>{" "}
              <span className="text-terminal-text">
                {new Date(latest.system_date).toLocaleString()}
              </span>
            </div>
            <div className="col-span-2">
              <span className="text-terminal-muted">Description:</span>{" "}
              <span className="text-terminal-text">
                {latest.description}
              </span>
            </div>
          </div>
          {latest.attributes && latest.attributes.length > 0 && (
            <div className="mt-3">
              <span className="text-xs text-terminal-muted uppercase tracking-wider">
                Supported Attributes
              </span>
              <div className="flex flex-wrap gap-2 mt-2">
                {latest.attributes.map((attr) => (
                  <span
                    key={attr}
                    className="text-xs bg-terminal-bg px-2 py-1 rounded border border-terminal-border text-terminal-cyan"
                  >
                    {attr}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div>
        <h2 className="text-sm font-bold text-terminal-muted uppercase tracking-wider mb-3">
          Version History ({versions.length} versions)
        </h2>
        <div className="space-y-2">
          {versions.map((v, i) => (
            <div
              key={i}
              className={`bg-terminal-surface border rounded p-3 text-xs ${
                i === 0
                  ? "border-terminal-green/30"
                  : "border-terminal-border"
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="text-terminal-muted">
                  {new Date(v.system_date).toLocaleString()}
                </span>
                <span className="text-terminal-text">{v.name}</span>
                {i === 0 && (
                  <span className="px-1.5 py-0.5 bg-terminal-green/20 text-terminal-green rounded text-[10px]">
                    LATEST
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
