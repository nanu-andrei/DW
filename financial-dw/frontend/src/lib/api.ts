const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(error || `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function fetchAssets(offset = 0, limit = 20) {
  return apiFetch(`/assets?offset=${offset}&limit=${limit}`);
}

export async function fetchAssetDetails(assetId: string) {
  return apiFetch(`/assets/${encodeURIComponent(assetId)}`);
}

export async function fetchDataSources(offset = 0, limit = 20) {
  return apiFetch(`/data-sources?offset=${offset}&limit=${limit}`);
}

export async function fetchDataSourceDetails(dsId: string) {
  return apiFetch(`/data-sources/${encodeURIComponent(dsId)}`);
}

export async function fetchTimeSeries(
  assetId: string,
  dataSourceId: string,
  startDate: string,
  endDate: string,
  includeAttributes = false
) {
  const params = new URLSearchParams({
    assetId,
    dataSourceId,
    startBusinessDate: startDate,
    endBusinessDate: endDate,
    includeAttributes: String(includeAttributes),
  });
  return apiFetch(`/data?${params}`);
}

export async function triggerIngestion(datasetCodes: string[], provider = "NASDAQ-DATA-LINK") {
  return apiFetch("/ingest", {
    method: "POST",
    body: JSON.stringify({ dataset_codes: datasetCodes, provider }),
  });
}

export async function runAggregation(dataSourceId: string) {
  return apiFetch("/analytics/aggregate", {
    method: "POST",
    body: JSON.stringify({ data_source_id: dataSourceId }),
  });
}

export async function runPrediction(assetId: string, dataSourceId: string) {
  return apiFetch("/analytics/predict", {
    method: "POST",
    body: JSON.stringify({ asset_id: assetId, data_source_id: dataSourceId }),
  });
}

export async function fetchTotals() {
  return apiFetch("/analytics/results/totals");
}

export async function fetchPredictions() {
  return apiFetch("/analytics/results/predictions");
}

export async function fetchModelMetrics() {
  return apiFetch("/analytics/results/metrics");
}
