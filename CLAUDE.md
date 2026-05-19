# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a data engineering pipeline for the **Olist Brazilian E-Commerce dataset**, using Google Cloud BigQuery as the data warehouse and dbt for SQL transformations. The pipeline flows: CSV files → BigQuery raw layer → dbt staging models → dbt mart models.

**GCP Project ID**: `dsai-module-2-project-496708`

## Environment Setup

Credentials are configured via `.env` at the project root, pointing to the GCP service account key JSON file. The notebook reads these via `python-dotenv`. Ensure the `.env` file and the service account JSON are present before running any pipeline steps.

## Key Commands

### Data Ingestion (run once)
The `notebooks/ingestion.ipynb` notebook loads all 9 CSV files from `data/` into BigQuery dataset `olist_raw`. It is idempotent (uses `if_exists='replace'`) but labeled "Run once only" — re-running will overwrite existing raw tables.

### dbt (from the `olist_dbt/` directory)
```bash
cd olist_dbt
dbt run                          # run all models
dbt run --select stg_orders      # run a single model
dbt test                         # run all tests
dbt compile                      # compile SQL without executing
dbt docs generate && dbt docs serve  # generate and view docs
```

The dbt profile is named `olist_dbt` and targets BigQuery. The profile configuration lives outside the repo in `~/.dbt/profiles.yml`.

## Architecture

### Layer Structure
| Layer | BigQuery Dataset | Location | Status |
|-------|-----------------|----------|--------|
| Raw | `olist_raw` | Loaded by `ingestion.ipynb` | Complete |
| Staging | `olist_raw` (same dataset, view materialization) | `olist_dbt/models/staging/` | In progress — only `stg_orders` exists |
| Marts | TBD | `olist_dbt/models/marts/` | Not started |

### Source Tables in BigQuery (`olist_raw`)
Nine tables loaded by the ingestion notebook: `orders`, `order_items`, `customers`, `products`, `sellers`, `payments`, `reviews`, `geolocation`, `category_translation`. All source definitions are in `olist_dbt/models/staging/sources.yml`.

### `stg_orders` Model
The only implemented staging model (`olist_dbt/models/staging/stg_orders.sql`). It casts timestamp columns and computes a `delivery_days` derived column from the raw orders table.

## Repository Notes

- `data/` and `logs/` are gitignored — raw CSVs and dbt logs are not tracked.
- The GCP service account key JSON (`dsai-module-2-project-496708-6b9c53a35141.json`) is gitignored but present locally — do not commit it.
- The entire `olist_dbt/` directory is currently untracked in git.
