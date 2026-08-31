import sqlite3

import pandas as pd

from pipeline import generate_sales, load_database


def test_generation_is_reproducible_and_valid():
    first = generate_sales(25, seed=7)
    second = generate_sales(25, seed=7)
    pd.testing.assert_frame_equal(first, second)
    assert len(first) == 25
    assert set(["order_id", "order_date", "customer_id", "region", "category", "revenue"]).issubset(first.columns)
    assert (first["revenue"] > 0).all()


def test_revenue_formula_and_database_round_trip(tmp_path):
    frame = generate_sales(10, seed=1)
    expected = (frame["quantity"] * frame["unit_price"] * (1 - frame["discount_pct"] / 100)).round(2)
    pd.testing.assert_series_equal(frame["revenue"], expected, check_names=False)
    database = tmp_path / "sales.db"
    load_database(frame, database)
    with sqlite3.connect(database) as connection:
        count = connection.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
    assert count == 10
