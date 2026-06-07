export interface PaginatedResponse<T = any> {
  items: T[];
  offset: number;
  limit: number;
  total: number;
  has_next: boolean;
}

export interface Asset {
  id: string;
  system_date: string;
  name: string;
  description: string;
  attributes: Record<string, string>;
  deleted: boolean;
}

export interface DataSource {
  id: string;
  system_date: string;
  name: string;
  description: string;
  attributes: string[];
}

export interface TimeSeriesRecord {
  businessDate: string;
  values: Record<string, number | string>;
}

export interface TimeSeriesResponse {
  data: {
    assetId: string;
    datasourceId: string;
    records: TimeSeriesRecord[];
  };
  attributes?: string[];
}

export interface IngestionRequest {
  dataset_codes: string[];
  provider: string;
}

export interface IngestionResult {
  fetched: number;
  stored: number;
  skipped: number;
  errors: number;
  status: string;
}

export interface AggregateResult {
  asset_id: string;
  business_date_year: number;
  cnt: number;
}

export interface PredictionResult {
  seconds: number;
  open: number;
  prediction: number;
}

export interface ModelMetrics {
  run_id: string;
  model_name: string;
  rmse: number;
  mae: number;
  r2: number;
  training_rows: number;
  feature_count: number;
  is_best: boolean;
}
