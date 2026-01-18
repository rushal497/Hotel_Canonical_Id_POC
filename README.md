# Hotel Identity Resolution & Deduplication Pipeline

## Overview

This project provides a robust pipeline for hotel data deduplication and canonicalization. It ingests raw hotel data, normalizes and enriches it with geocoding, detects duplicates using spatial and fuzzy logic, assigns canonical IDs, and outputs golden records for unique properties. Designed for scalability and stewardship, it supports multi-source ingestion, advanced normalization, multi-tier geocoding, and flexible reporting.

## Project Structure

```
hotel-deduplication/
├── data/
│   └── Hotel Data for Sorting.xlsx          ← Original file
├── src/
│   ├── main.py                  ← Main script to run everything
│   ├── geocoding.py             ← Geocoding functions
│   ├── distance.py              ← Haversine function
│   └── utils.py                 ← Helpers (normalization, etc.)
├── output/
│   ├── enriched_hotels.csv      ← Result with lat/long
│   ├── failed_geocoding.csv     ← Rows where both APIs failed
│   └── potential_duplicates.csv ← (future) clusters
├── requirements.txt             ← List of packages
└── README.md                    ← Instructions
```

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the main script:
   ```bash
   python src/main.py
   ```

## Future Work

- Implement clustering for potential duplicates.
- Enhance geocoding with fallback mechanisms.
- Add more robust normalization techniques.

## Pipeline Flow

```text
[1. Ingestion / Raw Data]
   Multiple sources → Excel / CSV / future database / API
   → Hotel Name, Address, City, Zip, GDS Code, etc.
          │
          ▼
[2. Pre-processing & Normalization Layer]
   - Load data
   - Basic cleaning (strip, lowercase)
   - Advanced normalization (address abbreviations, unicode, city synonyms)
   - Add unique row ID
          │
          ▼
[3. Geocoding Enrichment Layer]                     ← Multi-tier fallback
   For each row (parallelized):
   ┌────────────────────┐
   │ 1. Geocode.maps.co │ ── Success? ──► Save lat/lon + source
   └─────────┬──────────┘
             │ Fail
             ▼
   ┌────────────────────┐
   │ 2. LocationIQ      │ ── Success? ──► Save lat/lon + source
   └─────────┬──────────┘
             │ Fail
             ▼
   ┌────────────────────┐
   │ 3. Google Maps     │ ── Success? ──► Save lat/lon + source (optional paid)
   └─────────┬──────────┘
             │ All failed
             ▼
   Mark as geo_failed + log for retry/audit
          │
          ▼
[4. Duplicate Detection & Clustering Layer]
   Use spatial + exact + fuzzy signals:
   - Primary: Haversine distance ≤ 120 m (urban) or 300 m (rural)
   - Strong override: Exact same GDS code (when not null/0)
   - Safety filter: Names share core tokens OR fuzzy score ≥ 78%
   - Blocking: Group first by city (or lat/lon grid) for speed
   → Output: Groups (clusters) of row IDs that represent same physical hotel
          │
          ▼
[5. Canonical ID Assignment]
   - Each cluster gets one unique ID (e.g. CAN-000001)
   - Singletons (no matches) also get unique IDs
   - Store mapping: original row ID → Canonical ID
          │
          ▼
[6. Golden Record Creation (Optional – Recommended)]
   - For each cluster: pick the "best" row (most complete, highest geo confidence)
   - Or merge attributes (e.g., longest name, most common address)
   → Final golden table with one row per unique property
          │
          ▼
[7. Output & Reporting]
   - enriched_data.csv (intermediate)
   - canonical_mapping.csv (row → CAN ID)
   - golden_hotels.csv (one row per unique hotel)
   - failed_geocoding.csv
   - duplicate_report.txt / .csv (clusters summary)
   - Stewardship queue: uncertain matches (low confidence)
```
