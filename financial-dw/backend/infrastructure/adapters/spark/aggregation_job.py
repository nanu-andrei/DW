from pyspark.sql import SparkSession


def run_aggregation(
    cassandra_host: str, keyspace: str, data_source_filter: str
) -> int:
    spark = (
        SparkSession.builder.appName("Nanu DW - Compute Total")
        .config("spark.cassandra.connection.host", cassandra_host)
        .config(
            "spark.jars.packages",
            "com.datastax.spark:spark-cassandra-connector_2.12:3.5.0",
        )
        .getOrCreate()
    )

    df = (
        spark.read.format("org.apache.spark.sql.cassandra")
        .options(table="data", keyspace=keyspace)
        .load()
    )

    df.createOrReplaceTempView("ts_data")

    totals = spark.sql(
        f"""
        SELECT asset_id, business_date_year, COUNT(*) as cnt
        FROM ts_data
        WHERE data_source_id = '{data_source_filter}'
        GROUP BY asset_id, business_date_year
        ORDER BY asset_id, business_date_year
    """
    )

    totals.write.format("org.apache.spark.sql.cassandra").options(
        table="totals", keyspace=keyspace
    ).mode("append").save()

    result_count = totals.count()
    spark.stop()
    return result_count
