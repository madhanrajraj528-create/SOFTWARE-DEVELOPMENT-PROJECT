# Retail Sales Analytics Pipeline

A repeatable Python and SQLite analytics pipeline that generates synthetic retail transactions, stores them in a relational database, runs business queries, and produces Matplotlib charts. The project demonstrates data generation, ETL, SQL analysis, and visualization.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python pipeline.py --output-dir artifacts --rows 3000 --seed 42
```

The `--seed` option makes the generated dataset reproducible. The pipeline writes a CSV export, SQLite database, and three PNG visualizations to the selected output directory.

| Output | Purpose |
|---|---|
| `retail_sales.csv` | Transaction-level source data |
| `retail_sales.db` | SQLite database with indexed `sales` table |
| `monthly_revenue.png` | Monthly revenue trend |
| `revenue_by_category.png` | Revenue comparison by category |
| `revenue_by_region.png` | Revenue share by region |

## Data model

The `sales` table contains `order_id`, `order_date`, `customer_id`, `region`, `category`, `product`, `quantity`, `unit_price`, `discount_pct`, and calculated `revenue`. Revenue is calculated as `quantity × unit_price × (1 − discount_pct / 100)` and rounded to two decimal places.

## Testing

Run the automated checks with:

```bash
python -m pytest -q
```

The tests cover deterministic generation, schema presence, revenue calculation, and SQLite round-trip loading. Generated artifacts are intentionally excluded from version control so the repository remains lightweight.
