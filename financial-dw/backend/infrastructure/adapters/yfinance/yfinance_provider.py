"""
YFinance data provider adapter.

Fetches historical OHLCV data from Yahoo Finance using the yfinance library.
Dataset codes are ticker symbols (e.g. "BTC-USD", "ETH-USD", "AAPL").
"""

import asyncio
import logging
from datetime import datetime, timezone

import yfinance as yf

from domain.ports.data_provider import DataProviderPort, RawTimeSeriesPage
from infrastructure.config.settings import get_settings

logger = logging.getLogger(__name__)


class YFinanceProvider(DataProviderPort):
    """Implements DataProviderPort using Yahoo Finance (yfinance)."""

    PROVIDER_ID = "YFINANCE"

    def __init__(self, period: str | None = None):
        settings = get_settings()
        self._period = period or settings.yfinance_period

    async def fetch_dataset(
        self,
        dataset_code: str,
        cursor: str | None = None,
        page_size: int = 100,
    ) -> RawTimeSeriesPage:
        """
        Fetch historical data for a ticker symbol.

        yfinance returns all data at once (no cursor-based pagination),
        so we return everything in a single page with next_cursor=None.

        Args:
            dataset_code: Ticker symbol, e.g. "BTC-USD", "AAPL"
            cursor: Ignored (yfinance doesn't paginate)
            page_size: Ignored (yfinance returns full history for the period)
        """
        logger.info(
            f"Fetching {dataset_code} from Yahoo Finance (period={self._period})"
        )

        ticker = yf.Ticker(dataset_code)
        df = await asyncio.to_thread(ticker.history, period=self._period)

        if df.empty:
            logger.warning(f"No data returned for {dataset_code}")
            return RawTimeSeriesPage(
                records=[],
                columns=[],
                next_cursor=None,
                source_id=self.get_provider_id(),
                dataset_code=dataset_code,
            )

        # Reset index to make Date a column
        df = df.reset_index()

        # Normalize column name: yfinance returns "Date" or "Datetime"
        date_col = None
        for col in df.columns:
            if col.lower() in ("date", "datetime"):
                date_col = col
                break

        if date_col is None:
            raise ValueError(
                f"No date column found in yfinance data for {dataset_code}. "
                f"Columns: {list(df.columns)}"
            )

        # Convert to list of dicts with consistent "date" key
        records: list[dict] = []
        columns_set: set[str] = set()

        for _, row in df.iterrows():
            record: dict = {}
            # Normalize the date value
            date_val = row[date_col]
            if hasattr(date_val, "strftime"):
                record["date"] = date_val.strftime("%Y-%m-%d")
            else:
                record["date"] = str(date_val)[:10]

            # Add numeric columns
            for col in df.columns:
                if col == date_col:
                    continue
                val = row[col]
                if val is not None and not _is_nan(val):
                    record[col] = float(val)
                    columns_set.add(col)

            records.append(record)

        columns = ["date"] + sorted(columns_set)

        logger.info(
            f"Fetched {len(records)} records for {dataset_code}, "
            f"columns: {columns}"
        )

        return RawTimeSeriesPage(
            records=records,
            columns=columns,
            next_cursor=None,  # yfinance returns all data at once
            source_id=self.get_provider_id(),
            dataset_code=dataset_code,
        )

    def get_provider_id(self) -> str:
        return self.PROVIDER_ID


def _is_nan(val) -> bool:
    """Check if a value is NaN (works for float and numpy types)."""
    try:
        return val != val  # NaN != NaN is True
    except (TypeError, ValueError):
        return False
