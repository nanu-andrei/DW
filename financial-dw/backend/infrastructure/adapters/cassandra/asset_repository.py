import asyncio
from typing import Optional
from datetime import datetime, timezone

from domain.ports.asset_repository import AssetRepositoryPort
from domain.entities.asset import Asset
from domain.value_objects.pagination import Page, PageRequest
from infrastructure.adapters.cassandra.session import get_cassandra_session


class CassandraAssetRepository(AssetRepositoryPort):
    def __init__(self):
        self._session = get_cassandra_session()
        self._prep_save = self._session.prepare(
            "INSERT INTO asset (id, system_date, name, description, attributes) "
            "VALUES (?, ?, ?, ?, ?)"
        )
        self._prep_latest = self._session.prepare(
            "SELECT * FROM asset WHERE id = ? LIMIT 1"
        )
        self._prep_all = self._session.prepare(
            "SELECT * FROM asset WHERE id = ?"
        )

    async def save(self, asset: Asset) -> Asset:
        await asyncio.to_thread(
            self._session.execute,
            self._prep_save,
            [
                asset.id,
                asset.system_date,
                asset.name,
                asset.description,
                asset.attributes,
            ],
        )
        return asset

    async def find_latest(self, asset_id: str) -> Optional[Asset]:
        rows = await asyncio.to_thread(
            self._session.execute, self._prep_latest, [asset_id]
        )
        row = rows.one()
        if row is None:
            return None
        return self._row_to_entity(row)

    async def find_all_versions(self, asset_id: str) -> list[Asset]:
        rows = await asyncio.to_thread(
            self._session.execute, self._prep_all, [asset_id]
        )
        return [self._row_to_entity(r) for r in rows]

    async def find_all_ids(self, page_request: PageRequest) -> Page[str]:
        rows = list(
            await asyncio.to_thread(
                self._session.execute, "SELECT DISTINCT id FROM asset"
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

    async def delete(self, asset_id: str) -> None:
        deleted_asset = Asset(
            id=asset_id,
            system_date=datetime.now(timezone.utc),
            name="",
            description="",
            attributes={"deleted": "true"},
            deleted=True,
        )
        await self.save(deleted_asset)

    def _row_to_entity(self, row) -> Asset:
        attrs = dict(row.attributes) if row.attributes else {}
        is_deleted = attrs.get("deleted") == "true"
        return Asset(
            id=row.id,
            system_date=row.system_date,
            name=row.name or "",
            description=row.description or "",
            attributes=attrs,
            deleted=is_deleted,
        )
