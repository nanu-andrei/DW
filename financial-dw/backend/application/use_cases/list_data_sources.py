from domain.ports.data_source_repository import DataSourceRepositoryPort
from domain.value_objects.pagination import Page, PageRequest


class ListDataSourcesUseCase:
    def __init__(self, ds_repo: DataSourceRepositoryPort):
        self._ds_repo = ds_repo

    async def execute(self, page_request: PageRequest) -> Page[str]:
        return await self._ds_repo.find_all_ids(page_request)
