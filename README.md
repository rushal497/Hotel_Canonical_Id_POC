# Hotel Deduplication Project

## Overview

This project is designed to process and deduplicate hotel data. It includes geocoding, distance calculations, and utilities for normalization.

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
