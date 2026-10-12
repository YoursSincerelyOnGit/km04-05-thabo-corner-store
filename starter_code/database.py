"""
database.py
------------
Task 3: Build a relational database from your cleaned data.

This module covers KM-04 topics: Introduction to Databases (DBMS,
components, characteristics) and Structured Query Language (SQL).

Design notes:
    - Two tables: products (PK: product_id) and sales (PK: sale_id,
      FK: product_id -> products.product_id).
    - Foreign keys are enabled per-connection with PRAGMA foreign_keys = ON.
      SQLite disables FK enforcement by default — without this pragma the
      FK constraint is decorative.
    - create_tables() drops existing tables first so the pipeline can be
      re-run from scratch without UNIQUE constraint errors.
"""

import sqlite3


def get_connection(db_path: str = "store.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables(conn: sqlite3.Connection) -> None:
    conn.execute("DROP TABLE IF EXISTS sales")
    conn.execute("DROP TABLE IF EXISTS products")

    conn.execute("""
        CREATE TABLE products (
            product_id   TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            category     TEXT,
            unit_price   REAL,
            in_stock     INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE sales (
            sale_id        TEXT PRIMARY KEY,
            product_id     TEXT NOT NULL,
            quantity       INTEGER NOT NULL,
            sale_date      TEXT NOT NULL,
            payment_method TEXT,
            customer_type  TEXT,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)
    conn.commit()


def insert_products(conn: sqlite3.Connection, products_df) -> None:
    products_df.to_sql("products", conn, if_exists="append", index=False)
    conn.commit()


def insert_sales(conn: sqlite3.Connection, sales_df) -> None:
    sales_df.to_sql("sales", conn, if_exists="append", index=False)
    conn.commit()


def query_total_revenue_per_product(conn: sqlite3.Connection):
    """
    Business question: Which products generate the most revenue?
    Uses INNER JOIN + GROUP BY + SUM (aggregation).
    """
    sql = """
        SELECT p.product_name,
               ROUND(SUM(s.quantity * p.unit_price), 2) AS revenue
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        GROUP BY p.product_id, p.product_name
        ORDER BY revenue DESC
    """
    return conn.execute(sql).fetchall()


def query_best_selling_product(conn: sqlite3.Connection):
    """
    Business question: Which single product sold the most units?
    Uses INNER JOIN + GROUP BY + SUM + ORDER + LIMIT.
    """
    sql = """
        SELECT p.product_name,
               SUM(s.quantity) AS total_units
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        GROUP BY p.product_id, p.product_name
        ORDER BY total_units DESC
        LIMIT 1
    """
    return conn.execute(sql).fetchall()


def query_sales_by_payment_method(conn: sqlite3.Connection):
    """
    Business question: How are customers paying?
    Uses COUNT + GROUP BY.
    """
    sql = """
        SELECT payment_method, COUNT(*) AS num_sales
        FROM sales
        GROUP BY payment_method
        ORDER BY num_sales DESC
    """
    return conn.execute(sql).fetchall()


def query_custom_one(conn: sqlite3.Connection):
    """
    Business question: Which product categories earn the most revenue?
    Uses INNER JOIN + GROUP BY + SUM.
    """
    sql = """
        SELECT p.category,
               ROUND(SUM(s.quantity * p.unit_price), 2) AS revenue
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        GROUP BY p.category
        ORDER BY revenue DESC
    """
    return conn.execute(sql).fetchall()


def query_custom_two(conn: sqlite3.Connection):
    """
    Business question: Which products have never been sold?
    Uses LEFT JOIN to find products with no matching sales rows —
    useful for spotting dead stock.
    """
    sql = """
        SELECT p.product_id, p.product_name
        FROM products p
        LEFT JOIN sales s ON p.product_id = s.product_id
        WHERE s.sale_id IS NULL
        ORDER BY p.product_id
    """
    return conn.execute(sql).fetchall()