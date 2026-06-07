from fastapi import APIRouter, Depends, Query, HTTPException

from interfaces.api.dependencies import (
    get_list_assets_use_case,
    get_asset_details_use_case,
)
from interfaces.api.schemas.asset_schemas import AssetDetailResponse
from interfaces.api.schemas.common import PaginatedResponse
from domain.value_objects.pagination import PageRequest

router = APIRouter(prefix="/api/v1/assets", tags=["Assets"])


@router.get("", response_model=PaginatedResponse)
async def list_assets(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    use_case=Depends(get_list_assets_use_case),
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


@router.get("/{asset_id:path}", response_model=list[AssetDetailResponse])
async def get_asset_details(
    asset_id: str,
    use_case=Depends(get_asset_details_use_case),
):
    versions = await use_case.execute(asset_id)
    if not versions:
        raise HTTPException(
            status_code=404, detail=f"Asset '{asset_id}' not found"
        )
    return [AssetDetailResponse.from_entity(v) for v in versions]
