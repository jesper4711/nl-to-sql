# Regenerate the SQLite DB and write a standalone generator script + README.
import sqlite3
import uuid
import random
from datetime import datetime, timedelta
import os
import math
import pandas as pd
from textwrap import dedent

DB_PATH = "sales.db"
README_PATH = "README_sales_db.md"

# -----------------------
# Config (feel free to tweak)
# -----------------------
SEED = 42
N_CUSTOMERS = 1000
N_PRODUCTS = 200
N_ORDERS = 10000
MIN_ITEMS_PER_ORDER = 1
MAX_ITEMS_PER_ORDER = 5

START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 9, 30)  # up to just before current date

REGIONS = [
    "Nordics: Sweden",
    "Nordics: Norway",
    "Nordics: Denmark",
    "DACH: Germany",
    "DACH: Austria",
    "DACH: Switzerland",
    "US: West",
    "US: East",
    "UK & Ireland",
    "Southern Europe: Spain",
    "Southern Europe: Italy",
    "Benelux: Netherlands",
]

CATEGORIES = [
    "Electronics",
    "Home",
    "Apparel",
    "Sports",
    "Beauty",
    "Automotive",
    "Toys",
    "Outdoors",
]

PRODUCT_NAMES = {
    "Electronics": ["Smartphone", "Laptop", "Tablet", "Headphones", "Smartwatch", "Camera", "Monitor", "Keyboard"],
    "Home": ["Vacuum", "Air Purifier", "Coffee Maker", "Blender", "Microwave", "Toaster", "Lamp", "Heater"],
    "Apparel": ["T-Shirt", "Jeans", "Jacket", "Sneakers", "Dress", "Hoodie", "Socks", "Cap"],
    "Sports": ["Running Shoes", "Yoga Mat", "Dumbbells", "Bicycle Helmet", "Tennis Racket", "Football", "Basketball", "Swim Goggles"],
    "Beauty": ["Moisturizer", "Serum", "Shampoo", "Conditioner", "Perfume", "Sunscreen", "Lipstick", "Mascara"],
    "Automotive": ["Car Wax", "Motor Oil", "Air Freshener", "Wiper Blades", "Tire Inflator", "Dashboard Camera", "Phone Mount", "Seat Cover"],
    "Toys": ["RC Car", "Puzzle", "Action Figure", "Doll", "Board Game", "Building Blocks", "Kite", "Yo-yo"],
    "Outdoors": ["Tent", "Sleeping Bag", "Camping Stove", "Backpack", "Hiking Poles", "Water Filter", "Cooler", "Flashlight"],
}

FIRST_NAMES = ["Alex", "Taylor", "Jordan", "Morgan", "Casey", "Riley", "Jamie", "Cameron", "Drew", "Sam", "Avery", "Quinn", "Elliot", "Rowan", "Reese", "Hayden"]
LAST_NAMES = ["Smith", "Johnson", "Andersson", "Svensson", "Brown", "Garcia", "Müller", "Schmidt", "Williams", "Jones", "Davis", "Martinez", "Clark", "Lewis", "Walker", "Young"]

random.seed(SEED)

def rand_uuid():
    return str(uuid.uuid4())

def rand_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=seconds)

def price_for_category(cat: str) -> float:
    ranges = {
        "Electronics": (80, 2000),
        "Home": (20, 600),
        "Apparel": (5, 300),
        "Sports": (10, 500),
        "Beauty": (5, 200),
        "Automotive": (10, 400),
        "Toys": (5, 200),
        "Outdoors": (15, 800),
    }
    lo, hi = ranges.get(cat, (10, 200))
    r = random.random()
    price = math.exp(math.log(lo) + r * (math.log(hi) - math.log(lo)))
    return round(price, 2)

def make_customers(n=N_CUSTOMERS):
    customers = []
    for _ in range(n):
        cid = rand_uuid()
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        region = random.choice(REGIONS)
        customers.append((cid, name, region))
    return customers

def make_products(n=N_PRODUCTS):
    products = []
    for _ in range(n):
        pid = rand_uuid()
        cat = random.choice(CATEGORIES)
        pname = f"{random.choice(PRODUCT_NAMES[cat])} {random.randint(100, 999)}"
        price = price_for_category(cat)
        products.append((pid, pname, cat, price))
    return products

def gaussian_bias_today(date_obj):
    days_from_start = (date_obj - START_DATE).days
    total_days = (END_DATE - START_DATE).days + 1
    center = total_days * 0.85
    spread = total_days * 0.25
    return math.exp(-((days_from_start - center)**2) / (2*(spread**2)))

def random_order_date():
    for _ in range(10):
        dt = rand_date(START_DATE, END_DATE)
        if random.random() < gaussian_bias_today(dt):
            return dt
    return rand_date(START_DATE, END_DATE)

def make_orders(customers, n=N_ORDERS):
    orders = []
    for _ in range(n):
        oid = rand_uuid()
        cust_id, _, _ = random.choice(customers)
        order_date = random_order_date().date().isoformat()
        orders.append((oid, cust_id, order_date, 0.0))
    return orders

def make_order_items(orders, products):
    items = []
    for (oid, _, _, _) in orders:
        k = random.randint(MIN_ITEMS_PER_ORDER, MAX_ITEMS_PER_ORDER)
        prod_choices = random.sample(products, k)
        for (pid, _, _, price) in prod_choices:
            qty = random.randint(1, 5)
            discount = random.choice([0, 0, 0.05, 0.1, 0.15, 0.2])
            line_rev = round(qty * price * (1 - discount), 2)
            items.append((oid, pid, qty, line_rev))
    return items

def compute_order_totals(order_items):
    totals = {}
    for oid, _, _, rev in order_items:
        totals[oid] = totals.get(oid, 0.0) + rev
    return totals

def init_db(conn):
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode = WAL;")
    cur.execute("PRAGMA synchronous = NORMAL;")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Customers (
        customer_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        region TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Products (
        product_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        order_date TEXT NOT NULL,
        total_amount REAL NOT NULL,
        FOREIGN KEY(customer_id) REFERENCES Customers(customer_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Order_Items (
        order_id TEXT NOT NULL,
        product_id TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        revenue REAL NOT NULL,
        FOREIGN KEY(order_id) REFERENCES Orders(order_id),
        FOREIGN KEY(product_id) REFERENCES Products(product_id)
    );
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer_date ON Orders(customer_id, order_date);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_items_order ON Order_Items(order_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_items_product ON Order_Items(product_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON Products(category);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_customers_region ON Customers(region);")

    conn.commit()

def populate_db(conn, customers, products, orders, order_items):
    cur = conn.cursor()
    cur.executemany("INSERT INTO Customers(customer_id, name, region) VALUES (?, ?, ?);", customers)
    cur.executemany("INSERT INTO Products(product_id, name, category, price) VALUES (?, ?, ?, ?);", products)
    cur.executemany("INSERT INTO Orders(order_id, customer_id, order_date, total_amount) VALUES (?, ?, ?, ?);", orders)
    cur.executemany("INSERT INTO Order_Items(order_id, product_id, quantity, revenue) VALUES (?, ?, ?, ?);", order_items)
    conn.commit()

def generate_database(db_path=DB_PATH):
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    try:
        init_db(conn)
        customers = make_customers()
        products = make_products()
        orders = make_orders(customers)
        items = make_order_items(orders, products)
        totals = compute_order_totals(items)

        orders_updated = []
        for (oid, cid, odate, _old_total) in orders:
            orders_updated.append((oid, cid, odate, round(totals.get(oid, 0.0), 2)))

        populate_db(conn, customers, products, orders_updated, items)
    finally:
        conn.close()

# Generate DB
generate_database(DB_PATH)

# Create README
readme = dedent(f"""
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

- Data is synthetic and reproducible (seed={SEED}).
- Date range: {START_DATE.date().isoformat()} to {END_DATE.date().isoformat()}, biased toward more recent months.
- Regions include Nordics, DACH, US, UK/Ireland, Southern Europe, Benelux.
- Categories include: {", ".join(CATEGORIES)}.
- Sizes: Customers={N_CUSTOMERS}, Products={N_PRODUCTS}, Orders={N_ORDERS}, Items per order {MIN_ITEMS_PER_ORDER}-{MAX_ITEMS_PER_ORDER}.

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
""").strip()

with open(README_PATH, "w") as f:
    f.write(readme)

# Preview few rows
conn = sqlite3.connect(DB_PATH)
df_customers = pd.read_sql_query("SELECT * FROM Customers LIMIT 5;", conn)
df_products = pd.read_sql_query("SELECT * FROM Products LIMIT 5;", conn)
df_orders = pd.read_sql_query("SELECT * FROM Orders ORDER BY order_date DESC LIMIT 5;", conn)
df_items = pd.read_sql_query("SELECT * FROM Order_Items LIMIT 5;", conn)

print("Customers (preview):")
print(df_customers)
print("\nProducts (preview):")
print(df_products)
print("\nOrders (recent 5):")
print(df_orders)
print("\nOrder_Items (preview):")
print(df_items)

print(f"\nGenerated database at {DB_PATH}")
print(f"Generated README at {README_PATH}")