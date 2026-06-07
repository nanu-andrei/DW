from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from domain.entities.asset import Asset


class AssetSummaryResponse(BaseModel):
    id: str


class AssetDetailResponse(BaseModel):
    id: str
    system_date: datetime
    name: str
    description: str
    attributes: dict[str, str]
    deleted: bool = False

    @classmethod
    def from_entity(cls, asset: Asset) -> "AssetDetailResponse":
        return cls(
            id=asset.id,
            system_date=asset.system_date,
            name=asset.name,
            description=asset.description,
            attributes=asset.attributes,
            deleted=asset.deleted,
        )
