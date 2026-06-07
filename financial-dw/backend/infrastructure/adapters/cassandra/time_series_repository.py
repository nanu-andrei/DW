import asyncio
import asyncio
from datetime import date
from collections import defaultdict

from domain.ports.time_series_repository import TimeSeriesRepositoryPort
from domain.entities.time_series_point import TimeSeriesPoint
from infrastructure.adapters.cassandra.session import get_cassandra_session


class CassandraTimeSeriesRepository(TimeSeriesRepositoryPort):
    def __init__(self):
        self._session = get_cassandra_session()
        self._prep_save = self._session.prepare(
            "INSERT INTO data (asset_id, data_source_id, business_date_year, "
            "business_date, system_date, values_double, values_int, values_text, deleted) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        self._prep_range = self._session.prepare(
            "SELECT * FROM data WHERE asset_id = ? AND data_source_id = ? "
            "AND business_date_year = ? AND business_date >= ? AND business_date < ?"
        )

    async def save(self, point: TimeSeriesPoint) -> TimeSeriesPoint:
        await asyncio.to_thread(
            self._session.execute,
            self._prep_save,
            [
                point.asset_id,
                point.data_source_id,
                point.business_date_year,
                point.business_date,
                point.system_date,
                point.values_double,
                point.values_int,
                point.values_text,
                point.deleted,
            ],
        )
        return point

    async def save_batch(self, points: list[TimeSeriesPoint]) -> int:
        count = 0
        for point in points:
            await self.save(point)
            count += 1
        return count

    async def find_latest_by_date_range(
        self,
        asset_id: str,
        data_source_id: str,
        start_date: date,
        end_date: date,
    ) -> list[TimeSeriesPoint]:
        # Determine years spanned
        years = list(range(start_date.year, end_date.year + 1))

        all_rows: list = []
        for year in years:
            y_start = max(start_date, date(year, 1, 1))
            y_end = end_date if year == end_date.year else date(year + 1, 1, 1)
            rows = await asyncio.to_thread(
                self._session.execute,
                self._prep_range,
                [asset_id, data_source_id, year, y_start, y_end],
            )
            all_rows.extend(rows)

        # Group by business_date, keep latest system_date per group
        grouped: dict[date, list] = defaultdict(list)
        for row in all_rows:
            grouped[row.business_date].append(row)

        result: list[TimeSeriesPoint] = []
        for bdate in sorted(grouped.keys(), reverse=True):
            versions = sorted(
                grouped[bdate], key=lambda r: r.system_date, reverse=True
            )
            latest = versions[0]
            if getattr(latest, "deleted", False):
                continue
            result.append(self._row_to_entity(latest))

        return result

    def _row_to_entity(self, row) -> TimeSeriesPoint:
        return TimeSeriesPoint(
            asset_id=row.asset_id,
            data_source_id=row.data_source_id,
            business_date=row.business_date,
            business_date_year=row.business_date_year,
            system_date=row.system_date,
            values_double=dict(row.values_double) if row.values_double else {},
            values_int=dict(row.values_int) if row.values_int else {},
            values_text=dict(row.values_text) if row.values_text else {},
            deleted=row.deleted if row.deleted else False,
        )

    async def get_aggregation_totals(self) -> list[dict]:
        rows = await asyncio.to_thread(
            self._session.execute, "SELECT * FROM totals"
        )
        return [
            {
                "asset_id": r.asset_id,
                "business_date_year": r.business_date_year,
                "cnt": r.cnt,
            }
            for r in rows
        ]

    async def get_prediction_results(self) -> list[dict]:
        rows = await asyncio.to_thread(
            self._session.execute, "SELECT * FROM regression_results"
        )
        return [
            {
                "seconds": r.seconds,
                "open": r.open,
                "prediction": r.prediction,
            }
            for r in rows
        ]

    async def get_model_metrics(self) -> list[dict]:
        rows = await asyncio.to_thread(
            self._session.execute, "SELECT * FROM model_metrics"
        )
        return [
            {
                "run_id": r.run_id,
                "model_name": r.model_name,
                "rmse": r.rmse,
                "mae": r.mae,
                "r2": r.r2,
                "training_rows": r.training_rows,
                "feature_count": r.feature_count,
                "is_best": r.is_best,
            }
            for r in rows
        ]
