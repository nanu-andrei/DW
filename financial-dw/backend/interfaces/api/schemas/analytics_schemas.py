from pydantic import BaseModel
from typing import Optional


class AggregateRequest(BaseModel):
    data_source_id: str


class PredictRequest(BaseModel):
    asset_id: str
    data_source_id: str


class AggregateResultItem(BaseModel):
    asset_id: str
    business_date_year: int
    cnt: int


class PredictionResultItem(BaseModel):
    seconds: int
    open: float
    prediction: float


class ModelMetricsItem(BaseModel):
    run_id: str
    model_name: str
    rmse: float
    mae: float
    r2: float
    training_rows: int
    feature_count: int
    is_best: bool


class AnalyticsJobResponse(BaseModel):
    status: str = "completed"
    message: str = ""
    result_count: int = 0
