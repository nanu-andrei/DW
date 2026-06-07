from domain.ports.asset_repository import AssetRepositoryPort
from domain.value_objects.pagination import Page, PageRequest


class ListAssetsUseCase:
    def __init__(self, asset_repo: AssetRepositoryPort):
        self._asset_repo = asset_repo

    async def execute(self, page_request: PageRequest) -> Page[str]:
        return await self._asset_repo.find_all_ids(page_request)
