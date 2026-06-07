"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import DataGrid from "@/components/data/DataGrid";
import Pagination from "@/components/common/Pagination";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import ErrorBanner from "@/components/common/ErrorBanner";
import { fetchAssets, fetchAssetDetails } from "@/lib/api";
import type { PaginatedResponse, Asset } from "@/lib/types";

export default function AssetsPage() {
  const router = useRouter();
  const [data, setData] = useState<PaginatedResponse | null>(null);
  const [assetDetails, setAssetDetails] = useState<Record<string, Asset>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const limit = 20;

  const loadAssets = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = (await fetchAssets(offset, limit)) as PaginatedResponse;
      setData(res);

      // Load details for each asset
      const details: Record<string, Asset> = {};
      await Promise.all(
        res.items.map(async (id: string) => {
          try {
            const versions = (await fetchAssetDetails(id)) as Asset[];
            if (versions.length > 0) {
              details[id] = versions[0];
            }
          } catch {
            // Skip failed lookups
          }
        })
      );
      setAssetDetails(details);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load assets");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAssets();
  }, [offset]);

  const columns = [
    { key: "id", label: "Asset ID", width: "40%" },
    { key: "name", label: "Name", width: "20%" },
    { key: "description", label: "Description", width: "30%" },
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
        const detail = assetDetails[id];
        return {
          id,
          name: detail?.name || id.split("/").pop() || "",
          description: detail?.description || "",
          system_date: detail?.system_date || "",
        };
      })
    : [];

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-lg font-bold text-terminal-green tracking-wider">
          ASSETS
        </h1>
        <p className="text-xs text-terminal-muted mt-1">
          Financial instruments in the data warehouse
        </p>
      </div>

      {error && <ErrorBanner message={error} onRetry={loadAssets} />}

      <div className="bg-terminal-surface border border-terminal-border rounded">
        {loading ? (
          <LoadingSpinner />
        ) : (
          <>
            <DataGrid
              columns={columns}
              rows={rows}
              onRowClick={(row) =>
                router.push(`/assets/${encodeURIComponent(row.id)}`)
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
