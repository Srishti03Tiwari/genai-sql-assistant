# database/seed_data.py
import sqlite3
import os
from config import DB_PATH


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Load schema
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        cursor.executescript(f.read())

    # Seed customers
    customers = [
        ("Alice Johnson", "alice@example.com", "New York",  "USA"),
        ("Bob Smith",     "bob@example.com",   "London",    "UK"),
        ("Carla Diaz",    "carla@example.com", "Madrid",    "Spain"),
        ("David Lee",     "david@example.com", "Seoul",     "Korea"),
        ("Eva Brown",     "eva@example.com",   "Mumbai",    "India"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO customers (name, email, city, country) VALUES (?,?,?,?)",
        customers
    )

    # Seed products
    products = [
        ("Laptop Pro 15",  "Electronics", 1299.99, 50),
        ("Wireless Mouse", "Electronics",   29.99, 200),
        ("Office Chair",   "Furniture",    299.99,  30),
        ("Notebook 200pg", "Stationery",     4.99, 500),
        ("USB-C Hub",      "Electronics",   49.99, 150),
        ("Standing Desk",  "Furniture",    599.99,  20),
        ("Mechanical KB",  "Electronics",   89.99,  80),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO products (name, category, price, stock) VALUES (?,?,?,?)",
        products
    )

    # Seed orders
    orders = [
        (1, 1, 1, "2024-01-15", "delivered"),
        (2, 2, 3, "2024-01-20", "delivered"),
        (3, 3, 2, "2024-02-01", "shipped"),
        (4, 4, 1, "2024-02-10", "pending"),
        (1, 5, 2, "2024-02-15", "delivered"),
        (5, 1, 1, "2024-03-01", "cancelled"),
        (2, 7, 2, "2024-03-05", "delivered"),
        (3, 6, 1, "2024-03-10", "shipped"),
        (4, 2, 5, "2024-03-12", "delivered"),
        (5, 3, 1, "2024-03-15", "pending"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO orders (customer_id, product_id, quantity, order_date, status) VALUES (?,?,?,?,?)",
        orders
    )

    conn.commit()
    conn.close()
    print("✅ Database created and seeded successfully.")


if __name__ == "__main__":
    init_db()