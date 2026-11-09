import sqlite3
from pathlib import Path

DB = Path(__file__).parent / "data" / "company.db"
DB.parent.mkdir(parents=True, exist_ok=True)

schema = """
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    signup_date TEXT NOT NULL
);
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_price REAL NOT NULL
);
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);
CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    FOREIGN KEY(order_id) REFERENCES orders(order_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);
"""

customers = [
    (1, "Aarav Mehta", "Pune", "2024-01-12"),
    (2, "Diya Sharma", "Mumbai", "2024-02-03"),
    (3, "Kabir Patel", "Nashik", "2024-03-18"),
    (4, "Anaya Iyer", "Pune", "2024-04-21"),
    (5, "Vivaan Shah", "Aurangabad", "2024-05-09"),
    (6, "Ira Deshmukh", "Mumbai", "2024-06-14"),
    (7, "Reyansh Rao", "Pune", "2024-07-02"),
    (8, "Myra Kulkarni", "Nagpur", "2024-08-11"),
    (9, "Advik Joshi", "Nashik", "2024-09-23"),
    (10, "Sara Khan", "Aurangabad", "2024-10-05"),
]
products = [
    (1, "Wireless Mouse", "Accessories", 799.0),
    (2, "Mechanical Keyboard", "Accessories", 2499.0),
    (3, "USB-C Hub", "Accessories", 1799.0),
    (4, "27-inch Monitor", "Displays", 14999.0),
    (5, "Laptop Stand", "Furniture", 1299.0),
    (6, "Webcam HD", "Accessories", 2199.0),
    (7, "Office Chair", "Furniture", 8999.0),
    (8, "SSD 1TB", "Storage", 6499.0),
]
orders = [
    (1, 1, "2025-01-12", "delivered"), (2, 2, "2025-01-19", "delivered"),
    (3, 3, "2025-02-04", "delivered"), (4, 1, "2025-02-20", "delivered"),
    (5, 4, "2025-03-11", "delivered"), (6, 5, "2025-03-27", "delivered"),
    (7, 6, "2025-04-06", "delivered"), (8, 7, "2025-04-22", "delivered"),
    (9, 8, "2025-05-14", "delivered"), (10, 9, "2025-06-02", "delivered"),
    (11, 10, "2025-07-18", "delivered"), (12, 2, "2025-08-09", "delivered"),
    (13, 3, "2025-09-16", "shipped"), (14, 4, "2025-10-03", "delivered"),
    (15, 5, "2025-11-21", "delivered"), (16, 6, "2025-12-02", "delivered"),
]
items = [
    (1,1,1,2,799),(2,1,2,1,2499),(3,2,4,1,14999),(4,2,5,1,1299),
    (5,3,3,2,1799),(6,3,1,1,799),(7,4,8,1,6499),(8,4,6,1,2199),
    (9,5,7,1,8999),(10,5,5,2,1299),(11,6,2,1,2499),(12,6,3,1,1799),
    (13,7,4,1,14999),(14,7,1,2,799),(15,8,8,2,6499),(16,8,6,1,2199),
    (17,9,5,2,1299),(18,9,1,3,799),(19,10,7,1,8999),(20,10,2,1,2499),
    (21,11,4,1,14999),(22,11,3,1,1799),(23,12,8,1,6499),(24,12,5,1,1299),
    (25,13,6,2,2199),(26,13,1,1,799),(27,14,2,2,2499),(28,14,3,1,1799),
    (29,15,7,1,8999),(30,15,5,1,1299),(31,16,4,1,14999),(32,16,8,1,6499),
]

with sqlite3.connect(DB) as conn:
    conn.executescript(schema)
    conn.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", customers)
    conn.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products)
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", orders)
    conn.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", items)

print(f"Created sample database: {DB}")
