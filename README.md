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
