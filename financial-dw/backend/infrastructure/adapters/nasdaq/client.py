import httpx
from typing import Any


class NasdaqHttpClient:
    """HTTP client with retry and pagination handling for Nasdaq Data Link API."""

    def __init__(self, api_key: str, base_url: str, timeout: int = 30):
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        params = params or {}
        params["api_key"] = self._api_key
        url = f"{self._base_url}/{path}"
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
