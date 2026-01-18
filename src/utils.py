# utils.py
# Helper functions for normalization and other utilities

import unicodedata
import re

COMMON_ABBREVIATIONS = {
    'st.': 'street',
    'rd.': 'road',
    'ave.': 'avenue',
    'blvd.': 'boulevard',
    'dr.': 'drive',
    'ln.': 'lane',
    'hwy.': 'highway',
    'mt.': 'mount',
    'ctr.': 'center',
    'plz.': 'plaza',
    'sq.': 'square',
    'apt.': 'apartment',
    'fl.': 'floor',
}

CITY_SYNONYMS = {
    'nyc': 'new york',
    'sf': 'san francisco',
    'la': 'los angeles',
    'washington dc': 'washington',
}

def normalize_text(text):
    """Advanced normalization: strip, lowercase, unicode, abbreviations, city synonyms."""
    if not isinstance(text, str):
        return ''
    text = text.strip().lower()
    text = unicodedata.normalize('NFKC', text)
    # Replace abbreviations
    for abbr, full in COMMON_ABBREVIATIONS.items():
        text = re.sub(r'\b' + re.escape(abbr) + r'\b', full, text)
    # Replace city synonyms
    for syn, city in CITY_SYNONYMS.items():
        text = re.sub(r'\b' + re.escape(syn) + r'\b', city, text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text