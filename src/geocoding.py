# geocoding.py
# Functions for geocoding hotel addresses

import requests
import time

def geocode_address(address):
    """Geocode an address using external APIs."""
    pass

def geocode_maps_co(address, city, zip_code, api_key):
    query = f"{address}, {city}, {zip_code}".strip(", ")
    url = f"https://geocode.maps.co/search?q={requests.utils.quote(query)}&api_key={api_key}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data and len(data) > 0:
            best = data[0]
            return {
                'lat': float(best['lat']),
                'lon': float(best['lon']),
                'confidence': best.get('importance', 0.5)
            }
    except Exception:
        pass
    return None

def geocode_locationiq(address, city, zip_code, api_key):
    query = f"{address}, {city}, {zip_code}".strip(", ")
    url = f"https://us1.locationiq.com/v1/search?key={api_key}&q={requests.utils.quote(query)}&format=json"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if isinstance(data, list) and len(data) > 0:
            best = data[0]
            return {
                'lat': float(best['lat']),
                'lon': float(best['lon']),
                'confidence': float(best.get('importance', 0.5))
            }
    except Exception:
        pass
    return None

def enrich_row(row, maps_co_key, locationiq_key, delay=0.6):
    address = str(row.get('Hotel Address', ''))
    city = str(row.get('Hotel City', ''))
    zip_code = str(row.get('Hotel Zip', ''))
    gds_code = str(row.get('GDS Code', ''))

    # First attempt: full address
    result = geocode_maps_co(address, city, zip_code, maps_co_key)
    if result and result['confidence'] > 0.6:
        return result['lat'], result['lon'], 'maps_co', 'success'

    result = geocode_locationiq(address, city, zip_code, locationiq_key)
    if result and result['confidence'] > 0.5:
        return result['lat'], result['lon'], 'locationiq', 'success'

    # Fallback: omit zip code if missing or failed
    if not zip_code or not result:
        result = geocode_maps_co(address, city, '', maps_co_key)
        if result and result['confidence'] > 0.6:
            return result['lat'], result['lon'], 'maps_co_fallback', 'success'
        result = geocode_locationiq(address, city, '', locationiq_key)
        if result and result['confidence'] > 0.5:
            return result['lat'], result['lon'], 'locationiq_fallback', 'success'

    # Fallback: if GDS code is missing, try with just address and city
    if not gds_code or not result:
        result = geocode_maps_co(address, city, '', maps_co_key)
        if result and result['confidence'] > 0.6:
            return result['lat'], result['lon'], 'maps_co_gds_fallback', 'success'
        result = geocode_locationiq(address, city, '', locationiq_key)
        if result and result['confidence'] > 0.5:
            return result['lat'], result['lon'], 'locationiq_gds_fallback', 'success'

    time.sleep(delay)
    return None, None, 'none', 'failed'