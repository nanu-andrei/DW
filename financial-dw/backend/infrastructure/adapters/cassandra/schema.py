import logging

from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy

from infrastructure.config.settings import get_settings

logger = logging.getLogger(__name__)


def initialize_schema() -> None:
    """Initialize Cassandra keyspace and tables.
    
    Connects without a keyspace first to create it, then switches.
    """
    settings = get_settings()
    cluster = Cluster(
        contact_points=settings.cassandra_hosts,
        port=settings.cassandra_port,
        load_balancing_policy=DCAwareRoundRobinPolicy(local_dc="datacenter1"),
    )
    session = cluster.connect()

    logger.info("Creating keyspace if not exists...")
    session.execute(
        "CREATE KEYSPACE IF NOT EXISTS %s "
        "WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}"
        % settings.cassandra_keyspace
    )
    session.set_keyspace(settings.cassandra_keyspace)

    tables = [
        """
        CREATE TABLE IF NOT EXISTS asset (
            id TEXT,
            system_date TIMESTAMP,
            name TEXT,
            description TEXT,
            attributes MAP<TEXT, TEXT>,
            PRIMARY KEY (id, system_date)
        ) WITH CLUSTERING ORDER BY (system_date DESC)
        """,
        """
        CREATE TABLE IF NOT EXISTS data_source (
            id TEXT,
            system_date TIMESTAMP,
            name TEXT,
            description TEXT,
            attributes SET<TEXT>,
            PRIMARY KEY (id, system_date)
        ) WITH CLUSTERING ORDER BY (system_date DESC)
        """,
        """
        CREATE TABLE IF NOT EXISTS data (
            asset_id TEXT,
            data_source_id TEXT,
            business_date_year INT,
            business_date DATE,
            system_date TIMESTAMP,
            values_double MAP<TEXT, DOUBLE>,
            values_int MAP<TEXT, INT>,
            values_text MAP<TEXT, TEXT>,
            deleted BOOLEAN,
            PRIMARY KEY ((asset_id, data_source_id, business_date_year), business_date, system_date)
        ) WITH CLUSTERING ORDER BY (business_date DESC, system_date DESC)
        """,
        """
        CREATE TABLE IF NOT EXISTS totals (
            asset_id TEXT,
            business_date_year INT,
            cnt INT,
            PRIMARY KEY (asset_id, business_date_year)
        ) WITH CLUSTERING ORDER BY (business_date_year DESC)
        """,
        """
        CREATE TABLE IF NOT EXISTS regression_data (
            bdate DATE PRIMARY KEY,
            seconds INT,
            open DOUBLE,
            close DOUBLE,
            low DOUBLE,
            high DOUBLE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS regression_results (
            seconds INT PRIMARY KEY,
            open DOUBLE,
            prediction DOUBLE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS model_metrics (
            run_id TEXT,
            model_name TEXT,
            rmse DOUBLE,
            mae DOUBLE,
            r2 DOUBLE,
            training_rows INT,
            feature_count INT,
            is_best BOOLEAN,
            PRIMARY KEY (run_id, model_name)
        )
        """,
    ]

    for stmt in tables:
        session.execute(stmt.strip())

    logger.info("Schema initialized successfully")
    cluster.shutdown()
