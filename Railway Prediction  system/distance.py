"""
utils/distance.py
-----------------
Haversine-based geodesic distance calculation between two GPS coordinates.
Also exposes a wrapper that accepts (lat, lon) tuples for convenience.
"""

import math
from geopy.distance import geodesic


EARTH_RADIUS_KM = 6371.0


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute the great-circle distance (km) between two points on Earth
    using the Haversine formula.

    Parameters
    ----------
    lat1, lon1 : float  – origin coordinates (decimal degrees)
    lat2, lon2 : float  – destination coordinates (decimal degrees)

    Returns
    -------
    float  – distance in kilometres
    """
    # Convert degrees → radians
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def distance_between(point_a: tuple, point_b: tuple) -> float:
    """
    Geodesic distance (km) between two (lat, lon) tuples using geopy,
    which is slightly more accurate than pure Haversine over long distances.

    Falls back to our own haversine on import error.
    """
    try:
        return geodesic(point_a, point_b).kilometers
    except Exception:
        return haversine(*point_a, *point_b)


def bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute initial compass bearing (degrees, 0–360) from point 1 to point 2.
    Useful for the map arrow overlay.
    """
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)
    x = math.sin(dlambda) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda)
    theta = math.atan2(x, y)
    return (math.degrees(theta) + 360) % 360
