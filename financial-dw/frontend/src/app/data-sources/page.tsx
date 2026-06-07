"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import DataGrid from "@/components/data/DataGrid";
import Pagination from "@/components/common/Pagination";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import ErrorBanner from "@/components/common/ErrorBanner";
import { fetchDataSources, fetchDataSourceDetails } from "@/lib/api";
import type { PaginatedResponse, DataSource } from "@/lib/types";

export default function DataSourcesPage() {
  const router = useRouter();
  const [data, setData] = useState<PaginatedResponse | null>(null);
  const [dsDetails, setDsDetails] = useState<Record<string, DataSource>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const limit = 20;

  const loadDataSources = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = (await fetchDataSources(offset, limit)) as PaginatedResponse;
      setData(res);

      const details: Record<string, DataSource> = {};
      await Promise.all(
        res.items.map(async (id: string) => {
          try {
            const versions = (await fetchDataSourceDetails(id)) as DataSource[];
            if (versions.length > 0) {
              details[id] = versions[0];
            }
          } catch {
            // Skip
          }
        })
      );
      setDsDetails(details);
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Failed to load data sources"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDataSources();
  }, [offset]);

  const columns = [
    { key: "id", label: "Source ID", width: "30%" },
    { key: "name", label: "Name", width: "20%" },
    { key: "description", label: "Description", width: "30%" },
    {
      key: "attributeCount",
      label: "Attributes",
      width: "10%",
    },
    {
      key: "system_date",
      label: "Last Updated",
      width: "10%",
      render: (val: string) =>
        val ? new Date(val).toLocaleDateString() : "-",
    },
  ];

  const rows = data
    ? data.items.map((id: string) => {
        const detail = dsDetails[id];
        return {
          id,
          name: detail?.name || id,
          description: detail?.description || "",
          attributeCount: detail?.attributes?.length || 0,
          system_date: detail?.system_date || "",
        };
      })
    : [];

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-lg font-bold text-terminal-green tracking-wider">
          DATA SOURCES
        </h1>
        <p className="text-xs text-terminal-muted mt-1">
          Financial data providers configured in the warehouse
        </p>
      </div>

      {error && <ErrorBanner message={error} onRetry={loadDataSources} />}

      <div className="bg-terminal-surface border border-terminal-border rounded">
        {loading ? (
          <LoadingSpinner />
        ) : (
          <>
            <DataGrid
              columns={columns}
              rows={rows}
              onRowClick={(row) =>
                router.push(
                  `/data-sources/${encodeURIComponent(row.id)}`
                )
              }
            />
            {data && (
              <Pagination
                offset={data.offset}
                limit={data.limit}
                total={data.total}
                onPageChange={setOffset}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}
