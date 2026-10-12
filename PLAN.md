# PLAN.md — Thabo's Corner Store Sales Insights System

**Student:** Bandile Sithole
**Modules:** KM-04 (Data & Databases) + KM-05 (Programming & Python)

## 1. Decomposition — the biggest sub-problems

The project breaks into five sequential sub-problems, each in its own
starter_code module:

1. **Data cleaning** (`data_cleaning.py`) — the raw CSVs have missing
   values, four different date formats, inconsistent capitalisation,
   invalid foreign keys, and duplicate rows. Nothing else can proceed
   until this is trustworthy.
2. **Database design** (`database.py`) — a two-table relational schema
   (products / sales) with proper primary and foreign keys, loaded from
   the cleaned DataFrames, plus at least five SQL queries answering
   business questions.
3. **Programming logic** (`analysis.py`) — plain-Python functions using
   loops, conditionals, lists and dicts to compute summaries like the
   monthly sales trend and low-stock alerts.
4. **Visualisation** (`visualize.py`) — turn the SQL and analysis output
   into a bar chart (revenue per product) and a line chart (monthly
   trend).
5. **Security gate** (`security.py`) — SHA-256 password hashing and a
   login prompt so reports aren't publicly viewable.

Cross-cutting sub-problem: **version control** — commit after each task,
not once at the end.

## 2. Pattern recognition — what I expect to be messy

From reading the brief and skimming the CSVs:

- **products.csv**: 1 blank product name, 2 blank unit_prices, mixed
  category casing ("beverages" vs "Beverages"), and at least one exact
  duplicate row. Possible second Coca-Cola listing (P001 vs P015) —
  identical name and price but different IDs. I'll flag this in the
  README rather than silently delete.
- **sales.csv**: four date formats (`YYYY-MM-DD`, `DD/MM/YYYY`,
  `YYYY/MM/DD`, `DD-MM-YYYY`). One row (S0070, `14-02-2026`) proves the
  dash format is `DD-MM-YYYY` because 14 cannot be a month — so I'll
  standardise on **DD-MM-YYYY / DD/MM/YYYY = day-first** for all
  non-ISO rows. Also: ~13 blank dates, ~4 blank quantities, ~15 blank
  payment methods, 3 rows referencing P099 (a product that doesn't
  exist), and one exact duplicate (S0011).
- **Ambiguity decision (documented, not guessed):** ISO rows
  (`2026-01-01`) are unambiguous. For the slash and dash formats I'll
  assume day-first, justified by the S0070 row. This is written up in
  the README so the reasoning is auditable.

## 3. Abstraction — what I'm hiding away

- All SQL lives in `database.py` functions returning plain lists/dicts —
  `main.py` doesn't know or care that SQLite is underneath.
- All chart styling lives in `visualize.py` — `main.py` only passes
  labels and values.
- All password handling lives in `security.py` — `main.py` only asks
  "did they log in?".
- Reusable helper functions (e.g. `cleaning_summary`) rather than
  repeating `len()` comparisons.

## 4. Algorithm sketch — the order I'll work in

Bottom-up, because each layer depends on the one below it: