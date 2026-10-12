"""analysis.py — Task 4: plain-Python programming logic (KM-05)."""


def total_sales_records(sales_rows: list) -> int:
    """Count sales records using an explicit loop."""
    count = 0
    for row in sales_rows:
        count += 1
    return count


def low_stock_alert(products_rows: list, threshold: int = 5) -> list:
    """Return product names where in_stock is False."""
    alerts = []
    for product in products_rows:
        if product["in_stock"] is False or product["in_stock"] == 0:
            alerts.append(product["product_name"])
    return alerts


def monthly_sales_trend(sales_rows: list) -> dict:
    """Map 'YYYY-MM' to total quantity sold that month."""
    trend = {}
    for row in sales_rows:
        month = row["sale_date"][:7]
        if month in trend:
            trend[month] += row["quantity"]
        else:
            trend[month] = row["quantity"]
    return trend


def classify_transaction_size(quantity: int) -> str:
    """Bucket a quantity into Single / Multiple / Bulk / Invalid."""
    if quantity >= 5:
        return "Bulk"
    elif quantity >= 2:
        return "Multiple"
    elif quantity == 1:
        return "Single"
    else:
        return "Invalid"


def average_basket_size(sales_rows: list) -> float:
    """Average quantity per sale across all sales."""
    total = 0
    for row in sales_rows:
        total += row["quantity"]
    if len(sales_rows) == 0:
        return 0.0
    return round(total / len(sales_rows), 2)