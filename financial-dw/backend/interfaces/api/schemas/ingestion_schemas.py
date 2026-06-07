from pydantic import BaseModel, Field


class IngestionRequest(BaseModel):
    dataset_codes: list[str] = Field(
        ...,
        description="Ticker symbols to ingest, e.g. ['BTC-USD', 'ETH-USD', 'AAPL']",
        examples=[["BTC-USD", "ETH-USD"]],
    )
    provider: str = Field(
        default="YFINANCE",
        description="Data provider to use",
    )


class IngestionResponse(BaseModel):
    fetched: int
    stored: int
    skipped: int
    errors: int
    status: str = "completed"
