"""Repeatable retail-sales ETL and analysis pipeline.

Usage: python pipeline.py --output-dir artifacts --rows 3000 --seed 42
"""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

REGIONS = ["North", "South", "East", "West"]
CATEGORIES = ["Electronics", "Apparel", "Home & Kitchen", "Sports", "Beauty", "Books"]


def generate_sales(rows: int = 3000, seed: int = 42) -> pd.DataFrame:
    if rows < 1:
        raise ValueError("rows must be positive")
    rng = np.random.default_rng(seed)
    dates = pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 546, rows), unit="D")
    quantity = rng.integers(1, 7, rows)
    unit_price = np.round(rng.uniform(199, 5999, rows), 2)
    discount = rng.choice([0, 0, 0, 5, 10, 15, 20], rows)
    frame = pd.DataFrame({
        "order_id": np.arange(1000, 1000 + rows),
        "order_date": dates.strftime("%Y-%m-%d"),
        "customer_id": [f"C{n:04d}" for n in rng.integers(1, 501, rows)],
        "region": rng.choice(REGIONS, rows),
        "category": rng.choice(CATEGORIES, rows),
        "product": [f"Product {n:02d}" for n in rng.integers(1, 31, rows)],
        "quantity": quantity,
        "unit_price": unit_price,
        "discount_pct": discount,
    })
    frame["revenue"] = np.round(frame.quantity * frame.unit_price * (1 - frame.discount_pct / 100), 2)
    return frame


def load_database(frame: pd.DataFrame, database: Path) -> None:
    database.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database) as connection:
        frame.to_sql("sales", connection, if_exists="replace", index=False)
        connection.execute("CREATE INDEX IF NOT EXISTS idx_sales_order_date ON sales(order_date)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_sales_region_category ON sales(region, category)")


def query(database: Path, sql: str) -> pd.DataFrame:
    with sqlite3.connect(database) as connection:
        return pd.read_sql_query(sql, connection)


def create_charts(database: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    monthly = query(database, "SELECT substr(order_date, 1, 7) month, ROUND(SUM(revenue), 2) revenue FROM sales GROUP BY month ORDER BY month")
    monthly.plot(x="month", y="revenue", kind="line", marker="o", legend=False, figsize=(10, 4), title="Monthly Revenue")
    plt.ylabel("Revenue"); plt.tight_layout(); plt.savefig(output_dir / "monthly_revenue.png", dpi=150); plt.close()
    category = query(database, "SELECT category, ROUND(SUM(revenue), 2) revenue FROM sales GROUP BY category ORDER BY revenue DESC")
    category.plot(x="category", y="revenue", kind="bar", legend=False, figsize=(9, 4), title="Revenue by Category")
    plt.ylabel("Revenue"); plt.xticks(rotation=25, ha="right"); plt.tight_layout(); plt.savefig(output_dir / "revenue_by_category.png", dpi=150); plt.close()
    region = query(database, "SELECT region, ROUND(SUM(revenue), 2) revenue FROM sales GROUP BY region ORDER BY revenue DESC")
    region.set_index("region")["revenue"].plot(kind="pie", autopct="%1.1f%%", figsize=(6, 6), title="Revenue Share by Region", ylabel="")
    plt.tight_layout(); plt.savefig(output_dir / "revenue_by_region.png", dpi=150); plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--rows", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    frame = generate_sales(args.rows, args.seed)
    frame.to_csv(args.output_dir / "retail_sales.csv", index=False)
    database = args.output_dir / "retail_sales.db"
    load_database(frame, database)
    create_charts(database, args.output_dir)
    print(f"Generated {len(frame):,} rows in {args.output_dir}")


if __name__ == "__main__":
    main()
