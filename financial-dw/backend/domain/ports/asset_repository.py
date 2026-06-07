from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.asset import Asset
from domain.value_objects.pagination import Page, PageRequest


class AssetRepositoryPort(ABC):
    @abstractmethod
    async def save(self, asset: Asset) -> Asset: ...

    @abstractmethod
    async def find_latest(self, asset_id: str) -> Optional[Asset]: ...

    @abstractmethod
    async def find_all_versions(self, asset_id: str) -> list[Asset]: ...

    @abstractmethod
    async def find_all_ids(self, page_request: PageRequest) -> Page[str]: ...

    @abstractmethod
    async def delete(self, asset_id: str) -> None: ...
