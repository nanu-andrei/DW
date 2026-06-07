"""Unit tests for domain entities."""
import pytest
from datetime import datetime, date, timezone
from domain.entities.asset import Asset
from domain.entities.data_source import DataSource
from domain.entities.time_series_point import TimeSeriesPoint
from domain.entities.ingestion_result import IngestionResult
from domain.value_objects.pagination import PageRequest, Page
from domain.value_objects.asset_id import AssetId
from domain.value_objects.business_date import BusinessDate


class TestAsset:
    def test_create_new(self):
        asset = Asset.create_new("TEST/ASSET", "Test Asset", "A test", {"key": "val"})
        assert asset.id == "TEST/ASSET"
        assert asset.name == "Test Asset"
        assert asset.description == "A test"
        assert asset.attributes == {"key": "val"}
        assert asset.deleted is False
        assert isinstance(asset.system_date, datetime)

    def test_frozen(self):
        asset = Asset.create_new("ID", "Name", "Desc", {})
        with pytest.raises(AttributeError):
            asset.name = "New Name"  # type: ignore


class TestDataSource:
    def test_creation(self):
        ds = DataSource(
            id="SRC", system_date=datetime.now(timezone.utc),
            name="Source", description="Desc", attributes={"a", "b"},
        )
        assert ds.id == "SRC"
        assert "a" in ds.attributes


class TestTimeSeriesPoint:
    def test_creation(self):
        point = TimeSeriesPoint(
            asset_id="ASSET",
            data_source_id="SRC",
            business_date=date(2024, 1, 1),
            business_date_year=2024,
            system_date=datetime.now(timezone.utc),
            values_double={"price": 100.0},
        )
        assert point.asset_id == "ASSET"
        assert point.values_double["price"] == 100.0
        assert point.deleted is False


class TestIngestionResult:
    def test_defaults(self):
        result = IngestionResult()
        assert result.fetched == 0
        assert result.stored == 0


class TestPagination:
    def test_page_request(self):
        pr = PageRequest(offset=10, limit=5)
        assert pr.offset == 10

    def test_page_has_next(self):
        page = Page(items=["a", "b"], offset=0, limit=2, total=5)
        assert page.has_next is True

    def test_page_no_next(self):
        page = Page(items=["a"], offset=4, limit=2, total=5)
        assert page.has_next is False


class TestAssetId:
    def test_valid(self):
        aid = AssetId("TEST/ID")
        assert str(aid) == "TEST/ID"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            AssetId("")


class TestBusinessDate:
    def test_year(self):
        bd = BusinessDate(date(2024, 6, 15))
        assert bd.year == 2024
        assert str(bd) == "2024-06-15"
