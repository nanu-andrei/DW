"""Integration tests for the ingestion endpoint."""
import pytest

pytestmark = pytest.mark.skip(reason="Requires running backend services")


class TestIngestionAPI:
    def test_trigger_ingestion(self):
        """POST /api/v1/ingest should trigger ingestion pipeline."""
        pass
