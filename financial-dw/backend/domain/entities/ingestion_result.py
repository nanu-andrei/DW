from dataclasses import dataclass


@dataclass(frozen=True)
class IngestionResult:
    fetched: int = 0
    stored: int = 0
    skipped: int = 0
    errors: int = 0
