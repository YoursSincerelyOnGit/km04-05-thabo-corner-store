# Thabo's Corner Store — Sales Insights System (Starter Code)

This is your starting scaffold. It already contains the **shape** of the
project — file structure, function signatures, imports and docstrings —
so you can focus on the actual data, database and programming logic
described in the Project Brief.

## Folder structure

```
starter_code/
├── README.md              <- this file
├── requirements.txt        <- Python packages you need
├── main.py                 <- entry point; runs your whole pipeline
├── data_cleaning.py         <- Task 2: load & clean the raw CSVs
├── database.py              <- Task 3: build the SQLite database + SQL queries
├── analysis.py               <- Task 4: functions/loops/conditionals for insights
├── visualize.py               <- Task 5: charts with matplotlib
└── security.py                 <- Task 6: simple login / password hashing
```

## Before you start

1. Make sure Python 3.10+ is installed: `python3 --version`
2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the `data/` folder (provided separately) so it sits **next to**
   `starter_code/`, like this:
   ```
   project/
   ├── data/
   │   ├── products.csv
   │   └── sales.csv
   └── starter_code/
       └── ... (these files)
   ```

## Running your program

Once you've completed the TODOs in each file:

```bash
python main.py
```

## A note on the TODOs

Every function you need to complete has:
- A docstring explaining **what** it must do
- A `# TODO:` comment explaining **the specific steps**
- `raise NotImplementedError` as a placeholder — delete this once you've
  written your own code

Do not change the function names or the arguments they accept —
`main.py` calls them by name, and your facilitator's marking checklist
also references these exact names.

Good luck — and remember to commit your progress to GitHub regularly
as you complete each task, not just once at the end!
## Data Cleaning Decisions

### products.csv (16 raw → 14 clean, 2 rows removed)

- **P009 (blank product_name) — dropped.** A product with no name
  cannot appear in any report for Thabo, so the row is unusable.
- **P006 and P013 (blank unit_price) — filled with the median price of
  the same category.** Dropping them would lose valid sales records
  (P013 has eight sales). Median was chosen over mean because prices
  are skewed by high-value items like the R89 maize meal.
- **Category capitalisation standardised to Title Case** so that
  "beverages" and "Beverages" are treated as one category in SQL
  GROUP BY.
- **One exact duplicate row (P003) removed.** Note that P001 and P015
  are both "Coca-Cola 500ml" at R18.50 but with different product_ids —
  this is NOT treated as a duplicate because they have distinct primary
  keys, but it is flagged for Thabo to confirm with his supplier.

### sales.csv (71 raw → 51 clean, 20 rows removed)

**Date format decision (the important one):**
Raw dates appear in four formats: `YYYY-MM-DD`, `DD/MM/YYYY`,
`YYYY/MM/DD`, and `DD-MM-YYYY`. The dash format is ambiguous on its
own — `05-01-2026` could be 5 January or 1 May. Row **S0070
(`14-02-2026`)** resolves this: 14 cannot be a month, so the dash
format must be `DD-MM-YYYY` (day-first). By consistency, the slash
format is also day-first. All dates are standardised to ISO
`YYYY-MM-DD`. I chose day-first because South African date conventions
are day-first and because the data itself provides evidence for it —
this was a documented decision, not a silent guess.

- **14 rows with missing sale_date — dropped.** A sales record with no
  date cannot contribute to the monthly trend analysis or any
  time-based query, which are the primary business questions.
- **4 rows with missing quantity — dropped.** Revenue = quantity ×
  unit_price. Without a quantity, the row cannot be used in any
  meaningful aggregate.
- **3 rows referencing product_id P099 (does not exist in products) —
  dropped.** These rows would create orphaned foreign keys and break
  the JOIN in the revenue query.
- **14 rows with missing payment_method — filled with "Unknown".**
  Payment method is useful context but not essential for revenue or
  trend analysis. Dropping these rows would remove ~20% of the dataset
  for a non-critical field. "Unknown" is honest — it does not invent a
  payment method that was never recorded.
- **Missing customer_type — filled with "Unknown".** This is
  explicitly described in the brief as an optional context field.
- **One exact duplicate row (S0011) removed.**

The 20 removed rows include several that had more than one problem
(e.g. S0034 had no date, no quantity, and no payment method) — each
row is counted once even if it failed multiple checks.

## Database Design & SQL Queries

### Schema

**products** — `product_id` (TEXT, PRIMARY KEY), `product_name` (TEXT NOT NULL),
`category` (TEXT), `unit_price` (REAL), `in_stock` (INTEGER — 0 or 1, since
SQLite has no native boolean type)

**sales** — `sale_id` (TEXT, PRIMARY KEY), `product_id` (TEXT NOT NULL,
FOREIGN KEY → products.product_id), `quantity` (INTEGER NOT NULL),
`sale_date` (TEXT NOT NULL), `payment_method` (TEXT), `customer_type` (TEXT)

Foreign-key enforcement is enabled per-connection with
`PRAGMA foreign_keys = ON` — SQLite disables FK enforcement by default, so
without this pragma the FK constraint would be decorative. `create_tables()`
drops both tables before recreating them, so the pipeline is idempotent and
can be re-run without UNIQUE constraint errors.

### Query 1 — Revenue per product (JOIN + GROUP BY + SUM)

```sql
SELECT p.product_name,
       ROUND(SUM(s.quantity * p.unit_price), 2) AS revenue
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY revenue DESC;


QUERY 1 — Revenue per product
('5kg Maize Meal', 801.0)
('Eggs (6 pack)', 364.0)
('Lays Chips 100g', 352.0)
('Sunlight Dishwashing Liquid', 283.75)
('Bar One Chocolate', 224.0)
('Sugar 1kg', 220.5)
('Coca-Cola 500ml', 148.0)
('Airtime Voucher R10', 140.0)
('Simba Chips 120g', 132.0)
('Full Cream Milk 1L', 129.0)
('Fanta Orange 500ml', 111.0)
('Data Bundle 1GB', 98.0)
('Coca-Cola 500ml', 74.0)
('White Bread 700g', 48.0)

QUERY 2 — Best selling product
('Bar One Chocolate', 16)

QUERY 3 — Sales by payment method
('Cash', 18)
('Mobile Money', 12)
('Card', 12)
('Unknown', 9)

QUERY 4 — Revenue by category
('Household', 1305.25)
('Snacks', 708.0)
('Dairy', 493.0)
('Beverages', 333.0)
('Airtime & Data', 238.0)
('Bakery', 48.0)

QUERY 5 — Never-sold products

## Charts

### revenue_per_product.png
A bar chart showing total revenue (quantity × unit_price, summed across
all sales) per product, sorted highest first. It shows at a glance which
products carry the shop — 5kg Maize Meal, Eggs, and Lays Chips lead.

### monthly_trend.png
A line chart showing total units sold per month. It shows whether sales
are growing, flat, or falling month over month.

## CIA Triad Reflection

**Confidentiality.** The login gate protects confidentiality by requiring
a password before reports can be viewed. The password itself is never
stored — only its SHA-256 hash. Even if someone reads security.py, they
cannot reverse the hash back to the password. In a real system the hash
would live in a database with restricted access rather than hard-coded in
source; I noted this as a limitation.

**Integrity.** The login gate does not protect data integrity — a logged-in
user could still corrupt data. Integrity is instead enforced by the schema:
product_id and sale_id are PRIMARY KEYs (preventing duplicate sales),
sales.product_id is a FOREIGN KEY to products (preventing orphaned sales),
and NOT NULL constraints block incomplete records from entering the system.

**Availability.** The biggest availability risk is that this project lives
on one laptop with no backup. If the laptop dies, the data is lost. For a
real deployment I would recommend scheduled backups of store.db to cloud
storage, and moving the database to a shared machine or cloud service so
it isn't tied to a single device.

## Key Business Insights for Thabo

**Household goods carry the shop.** Household products (maize meal,
sugar, dishwashing liquid) made R1,305 of your total revenue — more than
double any other category. Snacks came second at R708. Never let your
household staples run out.

**Bar One Chocolate is your surprise best-seller** — 16 units sold,
more than any other product.

**Most customers pay in cash** (18 sales). Mobile Money and Card tied at
12 each. Only 9 sales had no payment method recorded. Card fees, if you
ever add them, would affect only a fifth of your customers.

**You have duplicate listings.** You have two Coca-Cola 500ml entries
(P001 and P015) with identical prices. Worth cleaning up in your
spreadsheet — it makes reports harder to read.

**You're losing data to gaps in your records.** Of 71 raw sales rows,
20 had to be dropped — missing dates, missing quantities, or references
to products that don't exist. Keeping dates in one consistent format
(YYYY-MM-DD) and never leaving a price or quantity blank would make
these reports more trustworthy.

**Your busiest month was January 2026** with 63 units sold, dropping to
54 in February. Worth watching whether that's seasonal (post-festive
lull) or a genuine slowdown.