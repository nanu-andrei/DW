from datetime import datetime, date, timezone

from domain.ports.asset_repository import AssetRepositoryPort
from domain.ports.data_source_repository import DataSourceRepositoryPort
from domain.ports.time_series_repository import TimeSeriesRepositoryPort
from domain.ports.data_provider import DataProviderPort
from domain.entities.asset import Asset
from domain.entities.data_source import DataSource
from domain.entities.time_series_point import TimeSeriesPoint
from domain.entities.ingestion_result import IngestionResult


class IngestDataUseCase:
    def __init__(
        self,
        provider: DataProviderPort,
        asset_repo: AssetRepositoryPort,
        ds_repo: DataSourceRepositoryPort,
        ts_repo: TimeSeriesRepositoryPort,
    ):
        self._provider = provider
        self._asset_repo = asset_repo
        self._ds_repo = ds_repo
        self._ts_repo = ts_repo

    async def execute(self, dataset_codes: list[str]) -> IngestionResult:
        fetched = 0
        stored = 0
        skipped = 0
        errors = 0

        for code in dataset_codes:
            asset_id = f"{self._provider.get_provider_id()}/{code}"
            ds_id = self._provider.get_provider_id()
            asset_ensured = False
            ds_ensured = False

            cursor = None
            while True:
                page = await self._provider.fetch_dataset(code, cursor=cursor)
                fetched += len(page.records)

                # Ensure asset exists (once per dataset)
                if not asset_ensured:
                    existing = await self._asset_repo.find_latest(asset_id)
                    if existing is None:
                        asset = Asset.create_new(
                            asset_id, code, f"Auto-ingested from {code}", {}
                        )
                        await self._asset_repo.save(asset)
                    asset_ensured = True

                # Ensure data source exists (once per dataset)
                if not ds_ensured:
                    existing_ds = await self._ds_repo.find_latest(ds_id)
                    if existing_ds is None:
                        ds = DataSource(
                            id=ds_id,
                            system_date=datetime.now(timezone.utc),
                            name=ds_id,
                            description=f"Provider {ds_id}",
                            attributes=set(page.columns),
                        )
                        await self._ds_repo.save(ds)
                    ds_ensured = True

                # Transform and load records
                points = []
                for record in page.records:
                    try:
                        point = self._transform_record(
                            record, page.columns, asset_id, ds_id
                        )
                        points.append(point)
                    except Exception:
                        errors += 1

                if points:
                    stored += await self._ts_repo.save_batch(points)

                cursor = page.next_cursor
                if cursor is None:
                    break

        return IngestionResult(
            fetched=fetched, stored=stored, skipped=skipped, errors=errors
        )

    def _transform_record(
        self,
        record: dict,
        columns: list[str],
        asset_id: str,
        ds_id: str,
    ) -> TimeSeriesPoint:
        bdate = date.fromisoformat(
            str(record.get("date", record.get("Date", "")))
        )
        values_double: dict[str, float] = {}
        values_text: dict[str, str] = {}
        for col in columns:
            if col.lower() == "date":
                continue
            val = record.get(col)
            if val is None:
                continue
            try:
                values_double[col] = float(val)
            except (ValueError, TypeError):
                values_text[col] = str(val)

        return TimeSeriesPoint(
            asset_id=asset_id,
            data_source_id=ds_id,
            business_date=bdate,
            business_date_year=bdate.year,
            system_date=datetime.now(timezone.utc),
            values_double=values_double,
            values_text=values_text,
        )
