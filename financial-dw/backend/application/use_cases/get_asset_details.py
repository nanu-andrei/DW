from domain.ports.asset_repository import AssetRepositoryPort
from domain.entities.asset import Asset

class GetAssetDetailsUseCase:
    def __init__(self, asset_repo: AssetRepositoryPort):
        self._asset_repo = asset_repo

    async def execute(self, asset_id: str) -> list[Asset]:
        return await self._asset_repo.find_all_versions(asset_id)
