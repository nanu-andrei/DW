import asyncio
from typing import Optional
from datetime import datetime

from domain.ports.data_source_repository import DataSourceRepositoryPort
from domain.entities.data_source import DataSource
from domain.value_objects.pagination import Page, PageRequest
from infrastructure.adapters.cassandra.session import get_cassandra_session


class CassandraDataSourceRepository(DataSourceRepositoryPort):
    def __init__(self):
        self._session = get_cassandra_session()
        self._prep_save = self._session.prepare(
            "INSERT INTO data_source (id, system_date, name, description, attributes) "
            "VALUES (?, ?, ?, ?, ?)"
        )
        self._prep_latest = self._session.prepare(
            "SELECT * FROM data_source WHERE id = ? LIMIT 1"
        )
        self._prep_all = self._session.prepare(
            "SELECT * FROM data_source WHERE id = ?"
        )

    async def save(self, data_source: DataSource) -> DataSource:
        await asyncio.to_thread(
            self._session.execute,
            self._prep_save,
            [
                data_source.id,
                data_source.system_date,
                data_source.name,
                data_source.description,
                data_source.attributes,
            ],
        )
        return data_source

    async def find_latest(self, ds_id: str) -> Optional[DataSource]:
        rows = await asyncio.to_thread(
            self._session.execute, self._prep_latest, [ds_id]
        )
        row = rows.one()
        if row is None:
            return None
        return self._row_to_entity(row)

    async def find_all_versions(self, ds_id: str) -> list[DataSource]:
        rows = await asyncio.to_thread(
            self._session.execute, self._prep_all, [ds_id]
        )
        return [self._row_to_entity(r) for r in rows]

    async def find_all_ids(self, page_request: PageRequest) -> Page[str]:
        rows = list(
            await asyncio.to_thread(
                self._session.execute, "SELECT DISTINCT id FROM data_source"
            )
        )
        all_ids = sorted([r.id for r in rows])
        total = len(all_ids)
        start = page_request.offset
        end = start + page_request.limit
        page_ids = all_ids[start:end]
        return Page(
            items=page_ids,
            offset=start,
            limit=page_request.limit,
            total=total,
        )

    def _row_to_entity(self, row) -> DataSource:
        return DataSource(
            id=row.id,
            system_date=row.system_date,
            name=row.name or "",
            description=row.description or "",
            attributes=set(row.attributes) if row.attributes else set(),
        )
