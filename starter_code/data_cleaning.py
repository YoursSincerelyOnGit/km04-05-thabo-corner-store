"""
data_cleaning.py
-----------------
Task 2: Load the raw CSV files and clean them.

This module covers KM-04 topics: Introduction to Data (data types,
errors of omission) and Data in Spreadsheets.

Date format decision (documented in README):
    Raw sale_date values come in four formats:
        YYYY-MM-DD, DD/MM/YYYY, YYYY/MM/DD, DD-MM-YYYY
    Row S0070 ("14-02-2026") proves the dash format must be DD-MM-YYYY
    (day-first), because 14 cannot be a month. By consistency, all
    non-ISO slash/dash values are treated as day-first. ISO values
    (YYYY-MM-DD) and YYYY/MM/DD values are unambiguous.
"""

import pandas as pd


def _parse_date(value):
    """Internal helper: parse one raw date string using day-first rules."""
    if value is None:
        return pd.NaT
    text = str(value).strip()
    if text == "" or text.lower() == "nan":
        return pd.NaT

    # ISO: YYYY-MM-DD
    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        return pd.to_datetime(text, format="%Y-%m-%d", errors="coerce")

    # YYYY/MM/DD
    if len(text) >= 10 and text[4] == "/" and text[7] == "/" and text[:4].isdigit():
        return pd.to_datetime(text, format="%Y/%m/%d", errors="coerce")

    # DD/MM/YYYY or DD-MM-YYYY — day-first (justified by S0070)
    normalised = text.replace("-", "/")
    return pd.to_datetime(normalised, format="%d/%m/%Y", errors="coerce")


def load_raw_data(products_path: str, sales_path: str):
    """Load both raw CSVs into pandas DataFrames."""
    products_df = pd.read_csv(products_path)
    sales_df = pd.read_csv(sales_path)
    return products_df, sales_df


def clean_products(products_df: "pd.DataFrame") -> "pd.DataFrame":
    """Clean the products DataFrame."""
    df = products_df.copy()

    # Drop rows with no product_name (unusable in any report)
    df = df[df["product_name"].notna() & (df["product_name"].astype(str).str.strip() != "")]

    # Fill missing unit_price with the median price of the same category,
    # falling back to the overall median if an entire category is blank
    df["unit_price"] = df.groupby("category")["unit_price"].transform(
        lambda x: x.fillna(x.median())
    )
    df["unit_price"] = df["unit_price"].fillna(df["unit_price"].median())

    # Standardise category capitalisation
    df["category"] = df["category"].astype(str).str.strip().str.title()

    # Remove exact duplicate rows
    df = df.drop_duplicates()

    return df.reset_index(drop=True)


def clean_sales(sales_df: "pd.DataFrame", valid_product_ids) -> "pd.DataFrame":
    """Clean the sales DataFrame."""
    df = sales_df.copy()

    # 1. Parse dates (day-first — see module docstring for justification)
    df["sale_date"] = df["sale_date"].apply(_parse_date)

    # 2. Drop rows we cannot analyse: no date, no quantity
    df = df[df["sale_date"].notna()]
    df = df[df["quantity"].notna()]

    # 3. Drop rows whose product_id is not in the cleaned products table
    df = df[df["product_id"].isin(valid_product_ids)]

    # 4. Fill missing payment_method and customer_type with "Unknown"
    df["payment_method"] = df["payment_method"].fillna("Unknown")
    df["customer_type"] = df["customer_type"].fillna("Unknown")

    # 5. Remove exact duplicate rows
    df = df.drop_duplicates()

    # 6. Types: quantity as int, sale_date as YYYY-MM-DD string
    df["quantity"] = df["quantity"].astype(int)
    df["sale_date"] = df["sale_date"].dt.strftime("%Y-%m-%d")

    return df.reset_index(drop=True)


def cleaning_summary(raw_df: "pd.DataFrame", clean_df: "pd.DataFrame", name: str) -> str:
    """Summarise how many rows were removed during cleaning."""
    removed = len(raw_df) - len(clean_df)
    return f"{name}: {len(raw_df)} raw rows -> {len(clean_df)} clean rows ({removed} removed)"