"""
data/stations.py
----------------
Static registry of well-known railway stations used to populate
the UI dropdowns and pre-fill lat/lon fields.

Coordinates are approximate centroids of the station areas.
"""

STATIONS: dict[str, dict] = {
    # ── Indian Railways ──────────────────────────────────────────────────
    "Mumbai CST":         {"lat": 18.9402, "lon": 72.8352, "code": "CSMT"},
    "Mumbai Dadar":       {"lat": 19.0178, "lon": 72.8478, "code": "DR"},
    "Pune Junction":      {"lat": 18.5285, "lon": 73.8742, "code": "PUNE"},
    "Nashik Road":        {"lat": 19.9975, "lon": 73.7898, "code": "NK"},
    "Surat":              {"lat": 21.2070, "lon": 72.8411, "code": "ST"},
    "Vadodara Junction":  {"lat": 22.3100, "lon": 73.1812, "code": "BRC"},
    "Ahmedabad Junction": {"lat": 23.0258, "lon": 72.5978, "code": "ADI"},
    "New Delhi":          {"lat": 28.6420, "lon": 77.2195, "code": "NDLS"},
    "Hazrat Nizamuddin":  {"lat": 28.5893, "lon": 77.2507, "code": "NZM"},
    "Agra Cantt":         {"lat": 27.1528, "lon": 78.0565, "code": "AGC"},
    "Mathura Junction":   {"lat": 27.4908, "lon": 77.6737, "code": "MTJ"},
    "Jaipur Junction":    {"lat": 26.9215, "lon": 75.7873, "code": "JP"},
    "Chennai Central":    {"lat": 13.0827, "lon": 80.2758, "code": "MAS"},
    "Bangalore City":     {"lat": 12.9783, "lon": 77.5707, "code": "SBC"},
    "Hyderabad Deccan":   {"lat": 17.3844, "lon": 78.4530, "code": "HYB"},
    "Kolkata Howrah":     {"lat": 22.5839, "lon": 88.3424, "code": "HWH"},
    "Bhubaneswar":        {"lat": 20.2663, "lon": 85.8438, "code": "BBS"},
    "Visakhapatnam":      {"lat": 17.6868, "lon": 83.2185, "code": "VSKP"},
    
}


def station_names() -> list[str]:
    return sorted(STATIONS.keys())


def get_station(name: str) -> dict:
    return STATIONS[name]
