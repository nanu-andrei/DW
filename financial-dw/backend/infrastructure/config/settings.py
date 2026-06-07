from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cassandra_hosts: list[str] = ["127.0.0.1"]
    cassandra_port: int = 9042
    cassandra_keyspace: str = "acme_dw"
    nasdaq_api_key: str = ""
    yfinance_period: str = "1y"
    spark_master_url: str = "spark://localhost:7077"
    app_name: str = "Nanu Financial DW"
    debug: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
