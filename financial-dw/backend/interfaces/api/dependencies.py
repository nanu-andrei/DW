from functools import lru_cache

from domain.ports.asset_repository import AssetRepositoryPort
from domain.ports.data_source_repository import DataSourceRepositoryPort
from domain.ports.time_series_repository import TimeSeriesRepositoryPort
from domain.ports.data_provider import DataProviderPort
from domain.ports.analytics_engine import AnalyticsEnginePort
from infrastructure.adapters.cassandra.asset_repository import CassandraAssetRepository
from infrastructure.adapters.cassandra.data_source_repository import CassandraDataSourceRepository
from infrastructure.adapters.cassandra.time_series_repository import CassandraTimeSeriesRepository
from infrastructure.adapters.yfinance.yfinance_provider import YFinanceProvider
from infrastructure.adapters.spark.spark_analytics import SparkAnalyticsAdapter
from application.use_cases.list_assets import ListAssetsUseCase
from application.use_cases.get_asset_details import GetAssetDetailsUseCase
from application.use_cases.list_data_sources import ListDataSourcesUseCase
from application.use_cases.get_data_source_details import GetDataSourceDetailsUseCase
from application.use_cases.get_time_series import GetTimeSeriesUseCase
from application.use_cases.ingest_data import IngestDataUseCase
from application.use_cases.run_aggregation import RunAggregationUseCase
from application.use_cases.run_prediction import RunPredictionUseCase
from application.use_cases.get_aggregation_results import GetAggregationResultsUseCase
from application.use_cases.get_prediction_results import GetPredictionResultsUseCase
from application.use_cases.get_model_metrics import GetModelMetricsUseCase


@lru_cache
def get_asset_repo() -> AssetRepositoryPort:
    return CassandraAssetRepository()


@lru_cache
def get_ds_repo() -> DataSourceRepositoryPort:
    return CassandraDataSourceRepository()


@lru_cache
def get_ts_repo() -> TimeSeriesRepositoryPort:
    return CassandraTimeSeriesRepository()


@lru_cache
def get_yfinance_provider() -> DataProviderPort:
    return YFinanceProvider()


@lru_cache
def get_analytics_engine() -> AnalyticsEnginePort:
    return SparkAnalyticsAdapter()


def get_list_assets_use_case() -> ListAssetsUseCase:
    return ListAssetsUseCase(asset_repo=get_asset_repo())


def get_asset_details_use_case() -> GetAssetDetailsUseCase:
    return GetAssetDetailsUseCase(asset_repo=get_asset_repo())


def get_list_data_sources_use_case() -> ListDataSourcesUseCase:
    return ListDataSourcesUseCase(ds_repo=get_ds_repo())


def get_data_source_details_use_case() -> GetDataSourceDetailsUseCase:
    return GetDataSourceDetailsUseCase(ds_repo=get_ds_repo())


def get_time_series_use_case() -> GetTimeSeriesUseCase:
    return GetTimeSeriesUseCase(ts_repo=get_ts_repo())


def get_ingest_use_case() -> IngestDataUseCase:
    return IngestDataUseCase(
        provider=get_yfinance_provider(),
        asset_repo=get_asset_repo(),
        ds_repo=get_ds_repo(),
        ts_repo=get_ts_repo(),
    )


def get_aggregation_use_case() -> RunAggregationUseCase:
    return RunAggregationUseCase(analytics=get_analytics_engine())


def get_prediction_use_case() -> RunPredictionUseCase:
    return RunPredictionUseCase(analytics=get_analytics_engine())


def get_aggregation_results_use_case() -> GetAggregationResultsUseCase:
    return GetAggregationResultsUseCase(ts_repo=get_ts_repo())


def get_prediction_results_use_case() -> GetPredictionResultsUseCase:
    return GetPredictionResultsUseCase(ts_repo=get_ts_repo())


def get_model_metrics_use_case() -> GetModelMetricsUseCase:
    return GetModelMetricsUseCase(ts_repo=get_ts_repo())
