#!/usr/bin/env python3
"""Optional seed script to populate the data warehouse with sample data.

Uses yfinance-compatible asset naming (ticker symbols as dataset codes).
"""

import sys
import os
from datetime import datetime, date, timedelta, timezone
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy
import random

CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST", "127.0.0.1")
CASSANDRA_PORT = int(os.environ.get("CASSANDRA_PORT", "9042"))
KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE", "acme_dw")

PROVIDER_ID = "YFINANCE"


def main():
    cluster = Cluster(
        contact_points=[CASSANDRA_HOST],
        port=CASSANDRA_PORT,
        load_balancing_policy=DCAwareRoundRobinPolicy(local_dc="datacenter1"),
    )
    session = cluster.connect(KEYSPACE)

    # Seed assets -- using yfinance ticker-based naming
    assets = [
        (f"{PROVIDER_ID}/BTC-USD", "BTC-USD", "Bitcoin / USD via Yahoo Finance"),
        (f"{PROVIDER_ID}/ETH-USD", "ETH-USD", "Ethereum / USD via Yahoo Finance"),
        (f"{PROVIDER_ID}/AAPL", "AAPL", "Apple Inc. via Yahoo Finance"),
    ]
    prep_asset = session.prepare(
        "INSERT INTO asset (id, system_date, name, description, attributes) VALUES (?, ?, ?, ?, ?)"
    )
    for aid, name, desc in assets:
        session.execute(prep_asset, [aid, datetime.now(timezone.utc), name, desc, {}])
    print(f"Seeded {len(assets)} assets")

    # Seed data source
    prep_ds = session.prepare(
        "INSERT INTO data_source (id, system_date, name, description, attributes) VALUES (?, ?, ?, ?, ?)"
    )
    ds_attrs = {"Open", "High", "Low", "Close", "Volume", "Dividends", "Stock Splits"}
    session.execute(
        prep_ds,
        [
            PROVIDER_ID,
            datetime.now(timezone.utc),
            "Yahoo Finance",
            "Yahoo Finance data via yfinance library",
            ds_attrs,
        ],
    )
    print("Seeded 1 data source (YFINANCE)")

    # Seed time series data
    prep_ts = session.prepare(
        "INSERT INTO data (asset_id, data_source_id, business_date_year, "
        "business_date, system_date, values_double, values_int, values_text, deleted) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    base_prices = {"BTC-USD": 30000.0, "ETH-USD": 2000.0, "AAPL": 180.0}
    count = 0
    for aid, name, _ in assets:
        base = base_prices[name]
        start = date(2023, 1, 1)
        for i in range(365):
            bdate = start + timedelta(days=i)
            # Skip weekends for stocks (not crypto)
            if name == "AAPL" and bdate.weekday() >= 5:
                continue
            price = base * (1 + random.uniform(-0.03, 0.03))
            high_val = price * 1.015
            low_val = price * 0.985
            open_val = price * (1 + random.uniform(-0.005, 0.005))
            volume = random.uniform(1000, 50000)
            values_double = {
                "Open": round(open_val, 2),
                "High": round(high_val, 2),
                "Low": round(low_val, 2),
                "Close": round(price, 2),
                "Volume": round(volume, 2),
            }
            session.execute(
                prep_ts,
                [
                    aid,
                    PROVIDER_ID,
                    bdate.year,
                    bdate,
                    datetime.now(timezone.utc),
                    values_double,
                    {},
                    {},
                    False,
                ],
            )
            count += 1
            base = price

    print(f"Seeded {count} time series records")
    cluster.shutdown()
    print("Done!")


if __name__ == "__main__":
    main()
