from fastapi import APIRouter, Depends

from interfaces.api.dependencies import get_ingest_use_case
from interfaces.api.schemas.ingestion_schemas import (
    IngestionRequest,
    IngestionResponse,
)

router = APIRouter(prefix="/api/v1/ingest", tags=["Ingestion"])


@router.post("", response_model=IngestionResponse)
async def trigger_ingestion(
    request: IngestionRequest,
    use_case=Depends(get_ingest_use_case),
):
    result = await use_case.execute(request.dataset_codes)
    return IngestionResponse(
        fetched=result.fetched,
        stored=result.stored,
        skipped=result.skipped,
        errors=result.errors,
        status="completed",
    )
