-- database/schema.sql

CREATE TABLE IF NOT EXISTS customers (
    customer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    city          TEXT,
    country       TEXT,
    created_at    DATE DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS products (
    product_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    category      TEXT,
    price         REAL NOT NULL,
    stock         INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS orders (
    order_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id   INTEGER REFERENCES customers(customer_id),
    product_id    INTEGER REFERENCES products(product_id),
    quantity      INTEGER NOT NULL,
    order_date    DATE DEFAULT CURRENT_DATE,
    status        TEXT DEFAULT 'pending'
);