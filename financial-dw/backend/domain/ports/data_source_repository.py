from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.data_source import DataSource
from domain.value_objects.pagination import Page, PageRequest


class DataSourceRepositoryPort(ABC):
    @abstractmethod
    async def save(self, data_source: DataSource) -> DataSource: ...

    @abstractmethod
    async def find_latest(self, ds_id: str) -> Optional[DataSource]: ...

    @abstractmethod
    async def find_all_versions(self, ds_id: str) -> list[DataSource]: ...

    @abstractmethod
    async def find_all_ids(self, page_request: PageRequest) -> Page[str]: ...
