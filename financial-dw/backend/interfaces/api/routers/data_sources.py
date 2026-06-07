from fastapi import APIRouter, Depends, Query, HTTPException

from interfaces.api.dependencies import (
    get_list_data_sources_use_case,
    get_data_source_details_use_case,
)
from interfaces.api.schemas.data_source_schemas import DataSourceDetailResponse
from interfaces.api.schemas.common import PaginatedResponse
from domain.value_objects.pagination import PageRequest

router = APIRouter(prefix="/api/v1/data-sources", tags=["Data Sources"])


@router.get("", response_model=PaginatedResponse)
async def list_data_sources(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    use_case=Depends(get_list_data_sources_use_case),
):
    page_request = PageRequest(offset=offset, limit=limit)
    page = await use_case.execute(page_request)
    return PaginatedResponse(
        items=page.items,
        offset=page.offset,
        limit=page.limit,
        total=page.total,
        has_next=page.has_next,
    )


@router.get("/{ds_id:path}", response_model=list[DataSourceDetailResponse])
async def get_data_source_details(
    ds_id: str,
    use_case=Depends(get_data_source_details_use_case),
):
    versions = await use_case.execute(ds_id)
    if not versions:
        raise HTTPException(
            status_code=404,
            detail=f"Data source '{ds_id}' not found",
        )
    return [DataSourceDetailResponse.from_entity(v) for v in versions]
