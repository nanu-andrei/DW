"""Unit tests for use cases with mock ports."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, date, timezone

from domain.entities.asset import Asset
from domain.entities.data_source import DataSource
from domain.entities.time_series_point import TimeSeriesPoint
from domain.value_objects.pagination import PageRequest, Page
from domain.ports.data_provider import RawTimeSeriesPage
from application.use_cases.list_assets import ListAssetsUseCase
from application.use_cases.get_asset_details import GetAssetDetailsUseCase
from application.use_cases.get_time_series import GetTimeSeriesUseCase
from application.use_cases.ingest_data import IngestDataUseCase


@pytest.fixture
def mock_asset_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_ds_repo():
    return AsyncMock()


@pytest.fixture
def mock_ts_repo():
    return AsyncMock()


@pytest.fixture
def mock_provider():
    provider = AsyncMock()
    provider.get_provider_id = MagicMock(return_value="TEST-PROVIDER")
    return provider


class TestListAssetsUseCase:
    @pytest.mark.asyncio
    async def test_returns_page(self, mock_asset_repo):
        expected = Page(items=["A", "B"], offset=0, limit=20, total=2)
        mock_asset_repo.find_all_ids.return_value = expected

        uc = ListAssetsUseCase(asset_repo=mock_asset_repo)
        result = await uc.execute(PageRequest())

        assert result.items == ["A", "B"]
        assert result.total == 2


class TestGetAssetDetailsUseCase:
    @pytest.mark.asyncio
    async def test_returns_versions(self, mock_asset_repo):
        versions = [
            Asset(id="X", system_date=datetime.now(timezone.utc), name="V2"),
            Asset(id="X", system_date=datetime(2024, 1, 1), name="V1"),
        ]
        mock_asset_repo.find_all_versions.return_value = versions

        uc = GetAssetDetailsUseCase(asset_repo=mock_asset_repo)
        result = await uc.execute("X")

        assert len(result) == 2
        assert result[0].name == "V2"


class TestGetTimeSeriesUseCase:
    @pytest.mark.asyncio
    async def test_returns_points(self, mock_ts_repo):
        points = [
            TimeSeriesPoint(
                asset_id="A", data_source_id="S",
                business_date=date(2024, 1, 1),
                business_date_year=2024,
                system_date=datetime.now(timezone.utc),
                values_double={"price": 100.0},
            )
        ]
        mock_ts_repo.find_latest_by_date_range.return_value = points

        uc = GetTimeSeriesUseCase(ts_repo=mock_ts_repo)
        result = await uc.execute("A", "S", date(2024, 1, 1), date(2024, 12, 31))

        assert len(result) == 1
        assert result[0].values_double["price"] == 100.0


class TestIngestDataUseCase:
    @pytest.mark.asyncio
    async def test_ingestion(self, mock_asset_repo, mock_ds_repo, mock_ts_repo, mock_provider):
        mock_asset_repo.find_latest.return_value = None
        mock_ds_repo.find_latest.return_value = None
        mock_ts_repo.save_batch.return_value = 2

        mock_provider.fetch_dataset.return_value = RawTimeSeriesPage(
            records=[
                {"date": "2024-01-01", "price": 100.0},
                {"date": "2024-01-02", "price": 101.0},
            ],
            columns=["date", "price"],
            next_cursor=None,
            source_id="TEST-PROVIDER",
            dataset_code="TEST",
        )

        uc = IngestDataUseCase(
            provider=mock_provider,
            asset_repo=mock_asset_repo,
            ds_repo=mock_ds_repo,
            ts_repo=mock_ts_repo,
        )
        result = await uc.execute(["TEST"])

        assert result.fetched == 2
        assert result.stored == 2
        assert result.errors == 0
