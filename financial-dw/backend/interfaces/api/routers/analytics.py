from fastapi import APIRouter, Depends, HTTPException

from interfaces.api.dependencies import (
    get_aggregation_use_case,
    get_prediction_use_case,
    get_aggregation_results_use_case,
    get_prediction_results_use_case,
    get_model_metrics_use_case,
)
from interfaces.api.schemas.analytics_schemas import (
    AggregateRequest,
    PredictRequest,
    AggregateResultItem,
    PredictionResultItem,
    ModelMetricsItem,
    AnalyticsJobResponse,
)

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.post("/aggregate", response_model=AnalyticsJobResponse)
async def run_aggregation(
    request: AggregateRequest,
    use_case=Depends(get_aggregation_use_case),
):
    try:
        results = await use_case.execute(request.data_source_id)
        return AnalyticsJobResponse(
            status="completed",
            message="Aggregation job finished successfully",
            result_count=len(results),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict", response_model=AnalyticsJobResponse)
async def run_prediction(
    request: PredictRequest,
    use_case=Depends(get_prediction_use_case),
):
    try:
        results = await use_case.execute(
            request.asset_id, request.data_source_id
        )
        return AnalyticsJobResponse(
            status="completed",
            message="Prediction job finished successfully",
            result_count=len(results),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/totals", response_model=list[AggregateResultItem])
async def get_totals(
    use_case=Depends(get_aggregation_results_use_case),
):
    results = await use_case.execute()
    return [
        AggregateResultItem(
            asset_id=r["asset_id"],
            business_date_year=r["business_date_year"],
            cnt=r["cnt"],
        )
        for r in results
    ]


@router.get(
    "/results/predictions", response_model=list[PredictionResultItem]
)
async def get_predictions(
    use_case=Depends(get_prediction_results_use_case),
):
    results = await use_case.execute()
    return [
        PredictionResultItem(
            seconds=r["seconds"], open=r["open"], prediction=r["prediction"]
        )
        for r in results
    ]


@router.get("/results/metrics", response_model=list[ModelMetricsItem])
async def get_model_metrics(
    use_case=Depends(get_model_metrics_use_case),
):
    """Get ML model evaluation metrics (RMSE, MAE, R-squared) for all trained models."""
    results = await use_case.execute()
    return [
        ModelMetricsItem(
            run_id=r["run_id"],
            model_name=r["model_name"],
            rmse=r["rmse"],
            mae=r["mae"],
            r2=r["r2"],
            training_rows=r["training_rows"],
            feature_count=r["feature_count"],
            is_best=r["is_best"],
        )
        for r in results
    ]
