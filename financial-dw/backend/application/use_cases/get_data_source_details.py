from domain.ports.data_source_repository import DataSourceRepositoryPort
from domain.entities.data_source import DataSource


class GetDataSourceDetailsUseCase:
    def __init__(self, ds_repo: DataSourceRepositoryPort):
        self._ds_repo = ds_repo

    async def execute(self, ds_id: str) -> list[DataSource]:
        return await self._ds_repo.find_all_versions(ds_id)
