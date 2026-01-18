import pandas as pd
from geocoding import enrich_row
from distance import haversine_distance
from deduplication import build_groups
from utils import normalize_text

# Replace with your real keys!
MAPS_CO_KEY = "696d0d4a41b9e039603292jbwd50a7b"
LOCATIONIQ_KEY = "pk.583d2079a29b73db9938a2752e8bd3c7"

print("Loading data...")
df = pd.read_excel("../data/Hotel Data for Sorting.xlsx")

print("Enriching with lat/long...")
df['Enriched_Lat'] = None
df['Enriched_Lon'] = None
df['Geo_Source'] = None
df['Geo_Status'] = None

failed = []

for idx, row in df.iterrows():
    lat, lon, source, status = enrich_row(row, MAPS_CO_KEY, LOCATIONIQ_KEY)
    df.at[idx, 'Enriched_Lat'] = lat
    df.at[idx, 'Enriched_Lon'] = lon
    df.at[idx, 'Geo_Source'] = source
    df.at[idx, 'Geo_Status'] = status
    
    if status == 'failed':
        failed.append(row.to_dict())

# Save results
df.to_csv("../output/enriched_hotels.csv", index=False)

if failed:
    pd.DataFrame(failed).to_csv("../output/failed_geocoding.csv", index=False)
    print(f"Saved {len(failed)} failed rows")

print("Done!")
print("Next step: review enriched_hotels.csv and failed_geocoding.csv")

# Add unique row ID
df['Row_Id'] = [f"ROW-{i+1:06d}" for i in range(len(df))]

# Advanced normalization
for col in ['Hotel Name', 'Hotel Address', 'Hotel City', 'Hotel Zip']:
    df[f'Norm_{col.replace(" ", "_")}'] = df[col].apply(normalize_text)

print("Building duplicate groups...")
# For blocking/grouping by city, pass normalized city to build_groups
city_blocks = df['Norm_Hotel_City'].unique()
grouped_results = {}
for city in city_blocks:
    city_df = df[df['Norm_Hotel_City'] == city]
    city_groups = build_groups(city_df)
    for cid, indices in city_groups.items():
        # Use composite key: city + group id
        new_cid = f"{city}_{cid}"
        grouped_results[new_cid] = list(indices)

# Assign canonical group ID to each row
id_map = {}
for cid, indices in grouped_results.items():
    for idx in indices:
        id_map[idx] = cid

df['Id'] = df.index.map(id_map.get)

# Remove any previous 'Canonical_Id' column if present
if 'Canonical_Id' in df.columns:
    df = df.drop(columns=['Canonical_Id'])

# Save results with Id and Row_Id
df.to_csv("../output/enriched_hotels.csv", index=False)

# Golden record selection: pick row with most non-null fields in each group
golden_rows = []
for cid, indices in grouped_results.items():
    group_df = df.loc[indices]
    # Score: count non-null fields
    best_row = group_df.notnull().sum(axis=1).idxmax()
    golden_rows.append(df.loc[best_row])
pd.DataFrame(golden_rows).to_csv("../output/golden_hotels.csv", index=False)

# Flag uncertain matches (low confidence)
uncertain = df[df['Geo_Status'] == 'failed']
uncertain.to_csv("../output/stewardship_queue.csv", index=False)

print("Done! Check output/groups_summary.txt")

# main.py
# Entry point for the hotel deduplication project

if __name__ == "__main__":
    print("Running Hotel Deduplication...")