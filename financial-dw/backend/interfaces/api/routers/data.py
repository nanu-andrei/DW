from datetime import date

from fastapi import APIRouter, Depends, Query, HTTPException

from interfaces.api.dependencies import (
    get_time_series_use_case,
    get_data_source_details_use_case,
)
from interfaces.api.schemas.time_series_schemas import (
    TimeSeriesResponse,
    TimeSeriesDataResponse,
    TimeSeriesRecord,
)

router = APIRouter(prefix="/api/v1/data", tags=["Time Series Data"])


@router.get("", response_model=TimeSeriesResponse)
async def get_time_series_data(
    assetId: str = Query(..., description="Asset identifier"),
    dataSourceId: str = Query(..., description="Data source identifier"),
    startBusinessDate: str = Query(..., description="Start date YYYY-MM-DD"),
    endBusinessDate: str = Query(..., description="End date YYYY-MM-DD"),
    includeAttributes: bool = Query(False, description="Include attribute list"),
    ts_use_case=Depends(get_time_series_use_case),
    ds_use_case=Depends(get_data_source_details_use_case),
):
    try:
        start = date.fromisoformat(startBusinessDate)
        end = date.fromisoformat(endBusinessDate)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD."
        )

    if (end - start).days > 365:
        raise HTTPException(
            status_code=400,
            detail="Date range cannot exceed 365 days.",
        )

    points = await ts_use_case.execute(assetId, dataSourceId, start, end)

    records = []
    for p in points:
        values: dict = {}
        values.update(p.values_double)
        values.update(p.values_int)
        values.update(p.values_text)
        records.append(
            TimeSeriesRecord(
                businessDate=p.business_date.isoformat(),
                values=values,
            )
        )

    attributes = None
    if includeAttributes:
        ds_versions = await ds_use_case.execute(dataSourceId)
        if ds_versions:
            attributes = sorted(ds_versions[0].attributes)

    return TimeSeriesResponse(
        data=TimeSeriesDataResponse(
            assetId=assetId,
            datasourceId=dataSourceId,
            records=records,
        ),
        attributes=attributes,
    )
