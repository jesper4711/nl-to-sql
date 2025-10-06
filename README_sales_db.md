# Synthetic Sales SQLite Database

This repository artifact contains a single-file SQLite database **sales.db** with four tables:

## Schema

**Customers**
- customer_id (TEXT, UUID primary key)
- name (TEXT)
- region (TEXT)

**Products**
- product_id (TEXT, UUID primary key)
- name (TEXT)
- category (TEXT)
- price (REAL)

**Orders**
- order_id (TEXT, UUID primary key)
- customer_id (TEXT, FK -> Customers.customer_id)
- order_date (TEXT, ISO date YYYY-MM-DD)
- total_amount (REAL)

**Order_Items**
- order_id (TEXT, FK -> Orders.order_id)
- product_id (TEXT, FK -> Products.product_id)
- quantity (INTEGER)
- revenue (REAL)

## Notes

- Data is synthetic and reproducible (seed=42).
- Date range: 2023-01-01 to 2025-09-30, biased toward more recent months.
- Regions include Nordics, DACH, US, UK/Ireland, Southern Europe, Benelux.
- Categories include: Electronics, Home, Apparel, Sports, Beauty, Automotive, Toys, Outdoors.
- Sizes: Customers=1000, Products=200, Orders=10000, Items per order 1-5.

## Quickstart (Python)

```python
import sqlite3
conn = sqlite3.connect("sales.db")
cur = conn.cursor()
cur.execute("SELECT category, SUM(revenue) FROM Order_Items oi JOIN Products p USING(product_id) GROUP BY category ORDER BY 2 DESC LIMIT 5;")
print(cur.fetchall())
```

## Example NL Questions

- "Which product category generated the most revenue in Q2 of 2024?"
- "List the top 5 customers by total spend in the last year."
- "Show the month-over-month growth in total orders for the Electronics category."
- "Which region had the lowest average order value in 2024?"
- "Find all customers who bought a Laptop but never a Smartphone."