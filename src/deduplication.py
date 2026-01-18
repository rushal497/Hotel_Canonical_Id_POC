# deduplication.py
import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree  # Replace KDTree with BallTree
from math import radians
from fuzzywuzzy import fuzz   # pip install fuzzywuzzy python-Levenshtein (faster)

DISTANCE_THRESHOLD_M = 120      # urban: 80-150, rural: 250-400
NAME_SIM_THRESHOLD = 75         # fuzzywuzzy score (0-100)

def normalize_name(name):
    if pd.isna(name): return ""
    name = str(name).lower().strip()
    # Remove common words (optional improvement)
    for word in ["hotel", "the", "inn", "resort", "by", "and", "international"]:
        name = name.replace(word, "").strip()
    return name

def are_related_names(name1, name2):
    if not name1 or not name2:
        return False
    sim = fuzz.token_set_ratio(name1, name2)  # good for word order differences
    return sim >= NAME_SIM_THRESHOLD

def build_groups(df):
    """
    Returns: dict of {canonical_id: list of row indices}
    """
    df = df.copy()
    df['norm_name'] = df['Hotel Name'].apply(normalize_name)
    
    # Prepare coords (only rows with valid lat/lon)
    valid_mask = df['Enriched_Lat'].notna() & df['Enriched_Lon'].notna()
    valid_df = df[valid_mask]
    
    if len(valid_df) == 0:
        print("No valid coordinates found!")
        return {}
    
    # Ensure latitude and longitude are numeric
    valid_df = valid_df.copy()  # Avoid SettingWithCopyWarning
    valid_df['Enriched_Lat'] = pd.to_numeric(valid_df['Enriched_Lat'], errors='coerce')
    valid_df['Enriched_Lon'] = pd.to_numeric(valid_df['Enriched_Lon'], errors='coerce')

    # Drop rows with invalid coordinates
    valid_df = valid_df.dropna(subset=['Enriched_Lat', 'Enriched_Lon'])

    # Verify data before conversion
    if valid_df.empty:
        print("No valid coordinates found after cleaning!")
        return {}

    # Convert to radians for haversine
    try:
        coords = np.deg2rad(valid_df[['Enriched_Lat', 'Enriched_Lon']].to_numpy(dtype=float))
    except Exception as e:
        print("Error during coordinate conversion:", e)
        return {}

    # Build BallTree (haversine metric)
    tree = BallTree(coords, metric='haversine')

    groups = {}
    canonical_id = 0
    used = set()

    for idx in valid_df.index:
        if idx in used:
            continue

        # Find all neighbors within threshold (in radians)
        neighbors_idx = tree.query_radius(
            coords[valid_df.index.get_loc(idx)].reshape(1, -1),
            r=DISTANCE_THRESHOLD_M / 6371000  # earth radius in meters
        )[0]

        # Filter real neighbors
        real_neighbors = valid_df.index[neighbors_idx]

        # Now apply name filter + GDS
        cluster = [idx]
        gds = df.at[idx, 'GDS Code']

        for candidate in real_neighbors:
            if candidate == idx:
                continue

            cand_gds = df.at[candidate, 'GDS Code']
            if (gds and cand_gds and gds == cand_gds) or \
               are_related_names(df.at[idx, 'norm_name'], df.at[candidate, 'norm_name']):
                cluster.append(candidate)

        # Assign group
        if len(cluster) > 1:
            for c in cluster:
                groups.setdefault(canonical_id, []).append(c)
                used.add(c)
            canonical_id += 1
        else:
            # Singleton
            groups.setdefault(canonical_id, []).append(idx)
            used.add(idx)
            canonical_id += 1

    # Add failed geo rows as singletons (future: handle separately)
    for idx in df[~valid_mask].index:
        groups.setdefault(canonical_id, []).append(idx)
        canonical_id += 1

    return groups