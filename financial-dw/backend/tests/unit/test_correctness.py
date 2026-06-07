"""Tests for temporal correctness, delete-as-insert, and ingestion flow."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date, timezone
from dataclasses import replace

from domain.entities.asset import Asset
from domain.entities.data_source import DataSource
from domain.entities.time_series_point import TimeSeriesPoint
from domain.entities.ingestion_result import IngestionResult
from domain.value_objects.pagination import PageRequest, Page
from domain.ports.data_provider import RawTimeSeriesPage
from application.use_cases.ingest_data import IngestDataUseCase
from application.use_cases.get_asset_details import GetAssetDetailsUseCase
from application.use_cases.get_time_series import GetTimeSeriesUseCase
from application.use_cases.get_aggregation_results import GetAggregationResultsUseCase
from application.use_cases.get_prediction_results import GetPredictionResultsUseCase


class TestTemporalSemantics:
    """Verify bi-temporal semantics work correctly."""

    def test_asset_create_new_sets_system_date(self):
        """Every new asset gets a system_date (temporal versioning)."""
        before = datetime.now(timezone.utc)
        asset = Asset.create_new("TEST", "Test", "Desc", {})
        after = datetime.now(timezone.utc)
        assert before <= asset.system_date <= after

    def test_asset_is_immutable(self):
        """Assets are frozen dataclasses -- no in-place updates."""
        asset = Asset.create_new("TEST", "Name", "Desc", {})
        with pytest.raises(AttributeError):
            asset.name = "Changed"  # type: ignore
        with pytest.raises(AttributeError):
            asset.system_date = datetime.now(timezone.utc)  # type: ignore

    def test_time_series_point_is_immutable(self):
        """TimeSeriesPoints are frozen -- no in-place updates."""
        point = TimeSeriesPoint(
            asset_id="A", data_source_id="S",
            business_date=date(2024, 1, 1),
            business_date_year=2024,
            system_date=datetime.now(timezone.utc),
        )
        with pytest.raises(AttributeError):
            point.deleted = True  # type: ignore


class TestDeleteAsInsert:
    """Verify soft-delete works via insert-with-deleted-flag pattern."""

    def test_deleted_asset_has_flag(self):
        """A deleted asset should have deleted=True and attributes marker."""
        deleted = Asset(
            id="TEST",
            system_date=datetime.now(timezone.utc),
            name="",
            description="",
            attributes={"deleted": "true"},
            deleted=True,
        )
        assert deleted.deleted is True
        assert deleted.attributes.get("deleted") == "true"

    def test_normal_asset_not_deleted(self):
        """A normal asset should have deleted=False."""
        asset = Asset.create_new("TEST", "Name", "Desc", {"key": "val"})
        assert asset.deleted is False


class TestIngestionOptimization:
    """Verify the ingestion use case only checks asset/ds existence once."""

    @pytest.mark.asyncio
    async def test_asset_checked_once_per_dataset(self):
        """Asset existence should only be checked once even with multi-page results."""
        mock_provider = AsyncMock()
        mock_provider.get_provider_id = MagicMock(return_value="YFINANCE")

        # Simulate 2 pages of data
        page1 = RawTimeSeriesPage(
            records=[{"date": "2024-01-01", "Close": 100.0}],
            columns=["date", "Close"],
            next_cursor="page2",
            source_id="YFINANCE",
            dataset_code="BTC-USD",
        )
        page2 = RawTimeSeriesPage(
            records=[{"date": "2024-01-02", "Close": 101.0}],
            columns=["date", "Close"],
            next_cursor=None,
            source_id="YFINANCE",
            dataset_code="BTC-USD",
        )
        mock_provider.fetch_dataset.side_effect = [page1, page2]

        mock_asset_repo = AsyncMock()
        mock_asset_repo.find_latest.return_value = None
        mock_ds_repo = AsyncMock()
        mock_ds_repo.find_latest.return_value = None
        mock_ts_repo = AsyncMock()
        mock_ts_repo.save_batch.return_value = 1

        uc = IngestDataUseCase(
            provider=mock_provider,
            asset_repo=mock_asset_repo,
            ds_repo=mock_ds_repo,
            ts_repo=mock_ts_repo,
        )
        result = await uc.execute(["BTC-USD"])

        # Asset and DS should be checked only once
        assert mock_asset_repo.find_latest.call_count == 1
        assert mock_ds_repo.find_latest.call_count == 1
        # But data should be saved from both pages
        assert mock_ts_repo.save_batch.call_count == 2
        assert result.fetched == 2
        assert result.stored == 2

    @pytest.mark.asyncio
    async def test_existing_asset_not_recreated(self):
        """If asset already exists, don't create a new one."""
        mock_provider = AsyncMock()
        mock_provider.get_provider_id = MagicMock(return_value="YFINANCE")
        mock_provider.fetch_dataset.return_value = RawTimeSeriesPage(
            records=[{"date": "2024-01-01", "Close": 100.0}],
            columns=["date", "Close"],
            next_cursor=None,
            source_id="YFINANCE",
            dataset_code="BTC-USD",
        )

        existing_asset = Asset.create_new("YFINANCE/BTC-USD", "BTC-USD", "Existing", {})
        mock_asset_repo = AsyncMock()
        mock_asset_repo.find_latest.return_value = existing_asset

        mock_ds_repo = AsyncMock()
        mock_ds_repo.find_latest.return_value = DataSource(
            id="YFINANCE",
            system_date=datetime.now(timezone.utc),
            name="Yahoo Finance",
            description="Existing",
        )

        mock_ts_repo = AsyncMock()
        mock_ts_repo.save_batch.return_value = 1

        uc = IngestDataUseCase(
            provider=mock_provider,
            asset_repo=mock_asset_repo,
            ds_repo=mock_ds_repo,
            ts_repo=mock_ts_repo,
        )
        await uc.execute(["BTC-USD"])

        # Should NOT save a new asset or data source
        mock_asset_repo.save.assert_not_called()
        mock_ds_repo.save.assert_not_called()


class TestAnalyticsUseCases:
    """Verify the new analytics results use cases work correctly."""

    @pytest.mark.asyncio
    async def test_aggregation_results(self):
        mock_ts_repo = AsyncMock()
        mock_ts_repo.get_aggregation_totals.return_value = [
            {"asset_id": "YFINANCE/BTC-USD", "business_date_year": 2024, "cnt": 365},
        ]
        uc = GetAggregationResultsUseCase(ts_repo=mock_ts_repo)
        results = await uc.execute()
        assert len(results) == 1
        assert results[0]["cnt"] == 365

    @pytest.mark.asyncio
    async def test_prediction_results(self):
        mock_ts_repo = AsyncMock()
        mock_ts_repo.get_prediction_results.return_value = [
            {"seconds": 1000, "open": 67000.0, "prediction": 67500.0},
        ]
        uc = GetPredictionResultsUseCase(ts_repo=mock_ts_repo)
        results = await uc.execute()
        assert len(results) == 1
        assert results[0]["prediction"] == 67500.0


class TestYFinanceIngestionValues:
    """Test that yfinance data values are correctly transformed."""

    @pytest.mark.asyncio
    async def test_ohlcv_values_preserved(self):
        """OHLCV values from yfinance should map to values_double correctly."""
        mock_provider = AsyncMock()
        mock_provider.get_provider_id = MagicMock(return_value="YFINANCE")
        mock_provider.fetch_dataset.return_value = RawTimeSeriesPage(
            records=[
                {
                    "date": "2024-06-01",
                    "Open": 67000.0,
                    "High": 68000.0,
                    "Low": 66500.0,
                    "Close": 67500.0,
                    "Volume": 25000.0,
                },
            ],
            columns=["date", "Close", "High", "Low", "Open", "Volume"],
            next_cursor=None,
            source_id="YFINANCE",
            dataset_code="BTC-USD",
        )

        mock_asset_repo = AsyncMock()
        mock_asset_repo.find_latest.return_value = None
        mock_ds_repo = AsyncMock()
        mock_ds_repo.find_latest.return_value = None
        mock_ts_repo = AsyncMock()
        mock_ts_repo.save_batch.return_value = 1

        uc = IngestDataUseCase(
            provider=mock_provider,
            asset_repo=mock_asset_repo,
            ds_repo=mock_ds_repo,
            ts_repo=mock_ts_repo,
        )
        await uc.execute(["BTC-USD"])

        # Check the saved time series points
        saved_points = mock_ts_repo.save_batch.call_args[0][0]
        assert len(saved_points) == 1
        point = saved_points[0]
        assert point.values_double["Open"] == 67000.0
        assert point.values_double["High"] == 68000.0
        assert point.values_double["Low"] == 66500.0
        assert point.values_double["Close"] == 67500.0
        assert point.values_double["Volume"] == 25000.0
        assert point.business_date == date(2024, 6, 1)
        assert point.business_date_year == 2024
        assert point.data_source_id == "YFINANCE"
        assert point.asset_id == "YFINANCE/BTC-USD"


class TestDataProviderPort:
    """Test the data provider port contract."""

    def test_raw_time_series_page_structure(self):
        page = RawTimeSeriesPage(
            records=[{"date": "2024-01-01", "Close": 100.0}],
            columns=["date", "Close"],
            next_cursor=None,
            source_id="TEST",
            dataset_code="ABC",
        )
        assert page.next_cursor is None
        assert len(page.records) == 1
        assert page.source_id == "TEST"

    def test_raw_time_series_page_with_cursor(self):
        page = RawTimeSeriesPage(
            records=[],
            columns=[],
            next_cursor="abc123",
            source_id="TEST",
            dataset_code="ABC",
        )
        assert page.next_cursor == "abc123"
