"""Tests for the YFinance data provider adapter."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

import pandas as pd

from infrastructure.adapters.yfinance.yfinance_provider import (
    YFinanceProvider,
    _is_nan,
)
from domain.ports.data_provider import RawTimeSeriesPage


@pytest.fixture
def sample_yfinance_df():
    """Create a DataFrame mimicking yfinance .history() output."""
    dates = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
    return pd.DataFrame(
        {
            "Date": dates,
            "Open": [100.0, 101.5, 102.0],
            "High": [105.0, 106.0, 107.0],
            "Low": [98.0, 99.0, 100.0],
            "Close": [103.0, 104.0, 105.5],
            "Volume": [1000000, 1200000, 1100000],
            "Dividends": [0.0, 0.0, 0.0],
            "Stock Splits": [0.0, 0.0, 0.0],
        }
    ).set_index("Date")


@pytest.fixture
def empty_df():
    """Empty DataFrame like yfinance returns for invalid tickers."""
    return pd.DataFrame()


class TestYFinanceProvider:
    @pytest.mark.asyncio
    async def test_provider_id(self):
        """Provider ID should be YFINANCE."""
        with patch(
            "infrastructure.adapters.yfinance.yfinance_provider.get_settings"
        ) as mock_settings:
            mock_settings.return_value = MagicMock(yfinance_period="1y")
            provider = YFinanceProvider()
            assert provider.get_provider_id() == "YFINANCE"

    @pytest.mark.asyncio
    async def test_fetch_dataset_returns_records(self, sample_yfinance_df):
        """fetch_dataset should convert yfinance DataFrame to RawTimeSeriesPage."""
        with patch(
            "infrastructure.adapters.yfinance.yfinance_provider.get_settings"
        ) as mock_settings, patch(
            "infrastructure.adapters.yfinance.yfinance_provider.yf"
        ) as mock_yf:
            mock_settings.return_value = MagicMock(yfinance_period="1y")
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = sample_yfinance_df
            mock_yf.Ticker.return_value = mock_ticker

            provider = YFinanceProvider()
            result = await provider.fetch_dataset("AAPL")

            assert isinstance(result, RawTimeSeriesPage)
            assert len(result.records) == 3
            assert result.source_id == "YFINANCE"
            assert result.dataset_code == "AAPL"
            assert result.next_cursor is None

    @pytest.mark.asyncio
    async def test_fetch_dataset_record_structure(self, sample_yfinance_df):
        """Each record should have date + numeric columns."""
        with patch(
            "infrastructure.adapters.yfinance.yfinance_provider.get_settings"
        ) as mock_settings, patch(
            "infrastructure.adapters.yfinance.yfinance_provider.yf"
        ) as mock_yf:
            mock_settings.return_value = MagicMock(yfinance_period="1y")
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = sample_yfinance_df
            mock_yf.Ticker.return_value = mock_ticker

            provider = YFinanceProvider()
            result = await provider.fetch_dataset("AAPL")

            first = result.records[0]
            assert "date" in first
            assert first["date"] == "2024-01-02"
            assert "Open" in first
            assert "High" in first
            assert "Low" in first
            assert "Close" in first
            assert "Volume" in first
            assert isinstance(first["Open"], float)
            assert first["Open"] == 100.0

    @pytest.mark.asyncio
    async def test_fetch_dataset_columns(self, sample_yfinance_df):
        """Columns should include date + all numeric columns sorted."""
        with patch(
            "infrastructure.adapters.yfinance.yfinance_provider.get_settings"
        ) as mock_settings, patch(
            "infrastructure.adapters.yfinance.yfinance_provider.yf"
        ) as mock_yf:
            mock_settings.return_value = MagicMock(yfinance_period="1y")
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = sample_yfinance_df
            mock_yf.Ticker.return_value = mock_ticker

            provider = YFinanceProvider()
            result = await provider.fetch_dataset("AAPL")

            assert result.columns[0] == "date"
            # Remaining columns sorted alphabetically
            non_date = result.columns[1:]
            assert non_date == sorted(non_date)
            assert "Open" in non_date
            assert "Close" in non_date

    @pytest.mark.asyncio
    async def test_fetch_dataset_empty(self, empty_df):
        """Empty ticker should return empty page."""
        with patch(
            "infrastructure.adapters.yfinance.yfinance_provider.get_settings"
        ) as mock_settings, patch(
            "infrastructure.adapters.yfinance.yfinance_provider.yf"
        ) as mock_yf:
            mock_settings.return_value = MagicMock(yfinance_period="1y")
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = empty_df
            mock_yf.Ticker.return_value = mock_ticker

            provider = YFinanceProvider()
            result = await provider.fetch_dataset("INVALID_TICKER")

            assert len(result.records) == 0
            assert result.columns == []
            assert result.next_cursor is None

    @pytest.mark.asyncio
    async def test_fetch_dataset_skips_nan(self):
        """NaN values should be excluded from records."""
        dates = pd.to_datetime(["2024-01-02"])
        df = pd.DataFrame(
            {
                "Date": dates,
                "Open": [100.0],
                "High": [float("nan")],
                "Low": [99.0],
                "Close": [101.0],
                "Volume": [float("nan")],
            }
        ).set_index("Date")

        with patch(
            "infrastructure.adapters.yfinance.yfinance_provider.get_settings"
        ) as mock_settings, patch(
            "infrastructure.adapters.yfinance.yfinance_provider.yf"
        ) as mock_yf:
            mock_settings.return_value = MagicMock(yfinance_period="1y")
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = df
            mock_yf.Ticker.return_value = mock_ticker

            provider = YFinanceProvider()
            result = await provider.fetch_dataset("TEST")

            record = result.records[0]
            assert "Open" in record
            assert "Low" in record
            assert "Close" in record
            # NaN values should be excluded
            assert "High" not in record
            assert "Volume" not in record

    @pytest.mark.asyncio
    async def test_custom_period(self):
        """Provider should respect custom period setting."""
        dates = pd.to_datetime(["2024-06-01"])
        df = pd.DataFrame(
            {"Date": dates, "Close": [150.0]}
        ).set_index("Date")

        with patch(
            "infrastructure.adapters.yfinance.yfinance_provider.get_settings"
        ) as mock_settings, patch(
            "infrastructure.adapters.yfinance.yfinance_provider.yf"
        ) as mock_yf:
            mock_settings.return_value = MagicMock(yfinance_period="6mo")
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = df
            mock_yf.Ticker.return_value = mock_ticker

            provider = YFinanceProvider()
            await provider.fetch_dataset("AAPL")

            mock_ticker.history.assert_called_once_with(period="6mo")


class TestIsNan:
    def test_float_nan(self):
        assert _is_nan(float("nan")) is True

    def test_normal_float(self):
        assert _is_nan(42.0) is False

    def test_zero(self):
        assert _is_nan(0.0) is False

    def test_string(self):
        assert _is_nan("hello") is False

    def test_none(self):
        assert _is_nan(None) is False


class TestYFinanceIngestionUseCase:
    """Test the full ingestion pipeline with yfinance-style data."""

    @pytest.mark.asyncio
    async def test_yfinance_ingestion_flow(self):
        """Simulate ingesting BTC-USD via yfinance provider mock."""
        from unittest.mock import AsyncMock, MagicMock
        from application.use_cases.ingest_data import IngestDataUseCase
        from domain.ports.data_provider import RawTimeSeriesPage

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
                {
                    "date": "2024-06-02",
                    "Open": 67500.0,
                    "High": 69000.0,
                    "Low": 67000.0,
                    "Close": 68800.0,
                    "Volume": 30000.0,
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
        mock_ts_repo.save_batch.return_value = 2

        uc = IngestDataUseCase(
            provider=mock_provider,
            asset_repo=mock_asset_repo,
            ds_repo=mock_ds_repo,
            ts_repo=mock_ts_repo,
        )
        result = await uc.execute(["BTC-USD"])

        # Verify results
        assert result.fetched == 2
        assert result.stored == 2
        assert result.errors == 0

        # Verify asset was created with yfinance naming
        mock_asset_repo.save.assert_called_once()
        saved_asset = mock_asset_repo.save.call_args[0][0]
        assert saved_asset.id == "YFINANCE/BTC-USD"
        assert saved_asset.name == "BTC-USD"

        # Verify data source was created
        mock_ds_repo.save.assert_called_once()
        saved_ds = mock_ds_repo.save.call_args[0][0]
        assert saved_ds.id == "YFINANCE"

        # Verify time series points were saved
        mock_ts_repo.save_batch.assert_called_once()
        points = mock_ts_repo.save_batch.call_args[0][0]
        assert len(points) == 2
        assert points[0].asset_id == "YFINANCE/BTC-USD"
        assert points[0].data_source_id == "YFINANCE"
        assert points[0].values_double["Open"] == 67000.0
        assert points[0].values_double["Close"] == 67500.0
        assert points[0].values_double["Volume"] == 25000.0
