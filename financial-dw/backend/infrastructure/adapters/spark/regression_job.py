"""
Spark ML prediction job with feature engineering and ensemble modeling.

Pipeline:
1. Extract OHLCV data from Cassandra
2. Engineer features: moving averages, volatility, price ratios, lag features
3. Train an ensemble of models (LinearRegression + GBTRegressor)
4. Evaluate with RMSE, MAE, R-squared
5. Store predictions and model metrics to Cassandra
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.regression import LinearRegression, GBTRegressor
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml import Pipeline


def run_prediction(
    cassandra_host: str, keyspace: str, asset_id: str, data_source_id: str
) -> dict:
    """
    Run a multi-model prediction pipeline on financial time series data.

    Returns a dict with prediction count and model evaluation metrics.
    """
    spark = (
        SparkSession.builder.appName("Nanu DW - ML Prediction Pipeline")
        .config("spark.cassandra.connection.host", cassandra_host)
        .config(
            "spark.jars.packages",
            "com.datastax.spark:spark-cassandra-connector_2.12:3.5.0",
        )
        .getOrCreate()
    )

    # ── Step 1: Extract raw OHLCV data ──────────────────────────────────
    raw = (
        spark.read.format("org.apache.spark.sql.cassandra")
        .options(table="data", keyspace=keyspace)
        .load()
    )

    raw.createOrReplaceTempView("spark_data")

    df = spark.sql(
        f"""
        SELECT values_double['Open'] as open,
               values_double['Close'] as close,
               values_double['Low'] as low,
               values_double['High'] as high,
               values_double['Volume'] as volume,
               cast(unix_timestamp(business_date) as int) as seconds,
               business_date as bdate
        FROM spark_data
        WHERE data_source_id = '{data_source_id}'
          AND asset_id = '{asset_id}'
          AND values_double['Open'] IS NOT NULL
        ORDER BY business_date ASC
    """
    ).na.drop()

    row_count = df.count()
    if row_count < 30:
        spark.stop()
        return {
            "prediction_count": 0,
            "error": f"Insufficient data: {row_count} rows (need >= 30)",
        }

    # Persist raw regression data
    df.write.format("org.apache.spark.sql.cassandra").options(
        table="regression_data", keyspace=keyspace
    ).mode("append").save()

    # ── Step 2: Feature engineering ─────────────────────────────────────
    window_spec = Window.orderBy("seconds")

    featured = df

    # Price ratios
    featured = featured.withColumn(
        "high_low_ratio", F.col("high") / F.col("low")
    )
    featured = featured.withColumn(
        "close_open_ratio", F.col("close") / F.col("open")
    )

    # Intraday range (volatility proxy)
    featured = featured.withColumn(
        "intraday_range", F.col("high") - F.col("low")
    )

    # Typical price
    featured = featured.withColumn(
        "typical_price",
        (F.col("high") + F.col("low") + F.col("close")) / 3.0,
    )

    # Moving averages (5-day, 10-day, 20-day)
    for window_size in [5, 10, 20]:
        w = Window.orderBy("seconds").rowsBetween(
            -(window_size - 1), 0
        )
        featured = featured.withColumn(
            f"sma_{window_size}",
            F.avg("close").over(w),
        )

    # Exponential-weighted volatility (rolling std of close, 10-day)
    vol_window = Window.orderBy("seconds").rowsBetween(-9, 0)
    featured = featured.withColumn(
        "volatility_10", F.stddev("close").over(vol_window)
    )

    # Lag features (previous day close, open)
    featured = featured.withColumn(
        "prev_close", F.lag("close", 1).over(window_spec)
    )
    featured = featured.withColumn(
        "prev_open", F.lag("open", 1).over(window_spec)
    )

    # Price momentum (close change from previous day)
    featured = featured.withColumn(
        "momentum",
        F.col("close") - F.col("prev_close"),
    )

    # Volume moving average ratio
    vol_ma_window = Window.orderBy("seconds").rowsBetween(-4, 0)
    featured = featured.withColumn(
        "volume_sma_5", F.avg("volume").over(vol_ma_window)
    )
    featured = featured.withColumn(
        "volume_ratio",
        F.when(F.col("volume_sma_5") > 0, F.col("volume") / F.col("volume_sma_5"))
        .otherwise(1.0),
    )

    # Drop rows with NaN from windowed features
    featured = featured.na.drop()

    # ── Step 3: Assemble features and scale ─────────────────────────────
    feature_cols = [
        "seconds",
        "close",
        "low",
        "high",
        "high_low_ratio",
        "close_open_ratio",
        "intraday_range",
        "typical_price",
        "sma_5",
        "sma_10",
        "sma_20",
        "volatility_10",
        "prev_close",
        "prev_open",
        "momentum",
        "volume_ratio",
    ]

    assembler = VectorAssembler(
        inputCols=feature_cols,
        outputCol="raw_features",
    )

    scaler = StandardScaler(
        inputCol="raw_features",
        outputCol="features",
        withStd=True,
        withMean=True,
    )

    # ── Step 4: Train/test split ────────────────────────────────────────
    assembled = assembler.transform(featured)
    scaler_model = scaler.fit(assembled)
    scaled = scaler_model.transform(assembled)

    train, test = scaled.randomSplit([0.7, 0.3], seed=42)

    # ── Step 5: Train multiple models ───────────────────────────────────
    results = {}

    # Model A: Regularized Linear Regression (ElasticNet)
    lr = LinearRegression(
        labelCol="open",
        featuresCol="features",
        maxIter=100,
        regParam=0.1,
        elasticNetParam=0.5,
        solver="normal",
    )
    lr_model = lr.fit(train)
    lr_predictions = lr_model.transform(test)
    results["linear_regression"] = _evaluate_model(lr_predictions, "open")

    # Model B: Gradient Boosted Trees Regressor
    gbt = GBTRegressor(
        labelCol="open",
        featuresCol="features",
        maxIter=50,
        maxDepth=5,
        stepSize=0.1,
        subsamplingRate=0.8,
        seed=42,
    )
    gbt_model = gbt.fit(train)
    gbt_predictions = gbt_model.transform(test)
    results["gbt_regressor"] = _evaluate_model(gbt_predictions, "open")

    # ── Step 6: Select best model and store predictions ─────────────────
    best_model_name = min(results, key=lambda k: results[k]["rmse"])
    best_predictions = (
        lr_predictions if best_model_name == "linear_regression" else gbt_predictions
    )

    # Store predictions from the best model
    prediction_output = best_predictions.select("seconds", "open", "prediction")
    prediction_output.write.format("org.apache.spark.sql.cassandra").options(
        table="regression_results", keyspace=keyspace
    ).mode("append").save()

    # ── Step 7: Store model metrics ─────────────────────────────────────
    metrics_rows = []
    for model_name, metrics in results.items():
        metrics_rows.append(
            (
                f"{asset_id}|{data_source_id}",
                model_name,
                float(metrics["rmse"]),
                float(metrics["mae"]),
                float(metrics["r2"]),
                int(row_count),
                len(feature_cols),
                model_name == best_model_name,
            )
        )

    metrics_df = spark.createDataFrame(
        metrics_rows,
        [
            "run_id",
            "model_name",
            "rmse",
            "mae",
            "r2",
            "training_rows",
            "feature_count",
            "is_best",
        ],
    )
    metrics_df.write.format("org.apache.spark.sql.cassandra").options(
        table="model_metrics", keyspace=keyspace
    ).mode("append").save()

    prediction_count = prediction_output.count()

    # ── Step 8: Log summary ─────────────────────────────────────────────
    lr_metrics = results["linear_regression"]
    gbt_metrics = results["gbt_regressor"]

    spark.stop()

    return {
        "prediction_count": prediction_count,
        "best_model": best_model_name,
        "models": {
            "linear_regression": {
                "rmse": lr_metrics["rmse"],
                "mae": lr_metrics["mae"],
                "r2": lr_metrics["r2"],
            },
            "gbt_regressor": {
                "rmse": gbt_metrics["rmse"],
                "mae": gbt_metrics["mae"],
                "r2": gbt_metrics["r2"],
            },
        },
        "feature_count": len(feature_cols),
        "training_rows": row_count,
    }


def _evaluate_model(predictions_df, label_col: str) -> dict:
    """Evaluate a model with standard regression metrics."""
    evaluator_rmse = RegressionEvaluator(
        labelCol=label_col,
        predictionCol="prediction",
        metricName="rmse",
    )
    evaluator_mae = RegressionEvaluator(
        labelCol=label_col,
        predictionCol="prediction",
        metricName="mae",
    )
    evaluator_r2 = RegressionEvaluator(
        labelCol=label_col,
        predictionCol="prediction",
        metricName="r2",
    )

    return {
        "rmse": evaluator_rmse.evaluate(predictions_df),
        "mae": evaluator_mae.evaluate(predictions_df),
        "r2": evaluator_r2.evaluate(predictions_df),
    }
