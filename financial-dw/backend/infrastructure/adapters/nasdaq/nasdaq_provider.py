import httpx
from domain.ports.data_provider import DataProviderPort, RawTimeSeriesPage
from infrastructure.config.settings import get_settings


class NasdaqDataProvider(DataProviderPort):
    BASE_URL = "https://data.nasdaq.com/api/v3/datatables"

    def __init__(self):
        self._api_key = get_settings().nasdaq_api_key

    async def fetch_dataset(
        self,
        dataset_code: str,
        cursor: str | None = None,
        page_size: int = 100,
    ) -> RawTimeSeriesPage:
        url = f"{self.BASE_URL}/{dataset_code}.json"
        params: dict = {
            "api_key": self._api_key,
            "qopts.per_page": page_size,
        }
        if cursor:
            params["qopts.cursor_id"] = cursor

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            body = resp.json()

        table = body.get("datatable", {})
        columns = [c["name"] for c in table.get("columns", [])]
        raw_rows = table.get("data", [])
        records = [dict(zip(columns, row)) for row in raw_rows]
        next_cursor = body.get("meta", {}).get("next_cursor_id")

        return RawTimeSeriesPage(
            records=records,
            columns=columns,
            next_cursor=next_cursor,
            source_id=self.get_provider_id(),
            dataset_code=dataset_code,
        )

    def get_provider_id(self) -> str:
        return "NASDAQ-DATA-LINK"
