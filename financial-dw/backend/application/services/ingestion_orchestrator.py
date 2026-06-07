from domain.ports.data_provider import DataProviderPort
from domain.ports.asset_repository import AssetRepositoryPort
from domain.ports.data_source_repository import DataSourceRepositoryPort
from domain.ports.time_series_repository import TimeSeriesRepositoryPort
from domain.entities.ingestion_result import IngestionResult
from application.use_cases.ingest_data import IngestDataUseCase


class IngestionOrchestrator:
    """Orchestrates the extract -> transform -> load pipeline."""

    def __init__(
        self,
        providers: list[DataProviderPort],
        asset_repo: AssetRepositoryPort,
        ds_repo: DataSourceRepositoryPort,
        ts_repo: TimeSeriesRepositoryPort,
    ):
        self._providers = providers
        self._asset_repo = asset_repo
        self._ds_repo = ds_repo
        self._ts_repo = ts_repo

    async def run(
        self, dataset_codes: list[str], provider_id: str | None = None
    ) -> IngestionResult:
        total = IngestionResult()
        for provider in self._providers:
            if provider_id and provider.get_provider_id() != provider_id:
                continue
            use_case = IngestDataUseCase(
                provider=provider,
                asset_repo=self._asset_repo,
                ds_repo=self._ds_repo,
                ts_repo=self._ts_repo,
            )
            result = await use_case.execute(dataset_codes)
            total = IngestionResult(
                fetched=total.fetched + result.fetched,
                stored=total.stored + result.stored,
                skipped=total.skipped + result.skipped,
                errors=total.errors + result.errors,
            )
        return total
