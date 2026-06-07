from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class Asset:
    id: str
    system_date: datetime
    name: str = ""
    description: str = ""
    attributes: dict[str, str] = field(default_factory=dict)
    deleted: bool = False

    @staticmethod
    def create_new(
        asset_id: str,
        name: str,
        description: str,
        attributes: dict[str, str],
    ) -> "Asset":
        return Asset(
            id=asset_id,
            system_date=datetime.now(timezone.utc),
            name=name,
            description=description,
            attributes=attributes,
        )
