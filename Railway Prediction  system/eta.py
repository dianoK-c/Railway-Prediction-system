"""
utils/eta.py
------------
Pure-physics ETA and ML-enhanced ETA calculation.

Physics ETA   : distance / speed  (baseline)
ML-enhanced   : LinearRegression trained on historical run data,
                using [distance_km, speed_kmh, delay_minutes] as features.
"""

from __future__ import annotations

import datetime
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Physics-based ETA (no ML, always available)
# ---------------------------------------------------------------------------

def physics_eta_minutes(distance_km: float, speed_kmh: float) -> float:
    """
    Compute travel time in minutes using simple kinematics.

    Parameters
    ----------
    distance_km : float  – remaining distance to next station
    speed_kmh   : float  – current train speed

    Returns
    -------
    float  – estimated minutes to arrival (0 if already at station)
    """
    if speed_kmh <= 0:
        return float("inf")           # Train is stationary
    return max(0.0, (distance_km / speed_kmh) * 60.0)


def compute_arrival_time(
    eta_minutes: float,
    reference_time: Optional[datetime.datetime] = None,
) -> datetime.datetime:
    """
    Add `eta_minutes` to `reference_time` (defaults to now) and return
    the wall-clock arrival datetime.
    """
    if reference_time is None:
        reference_time = datetime.datetime.now()
    return reference_time + datetime.timedelta(minutes=eta_minutes)


def compute_delay_minutes(
    scheduled_arrival: datetime.datetime,
    predicted_arrival: datetime.datetime,
) -> float:
    """
    Return delay in minutes (positive = late, negative = early).
    """
    delta = predicted_arrival - scheduled_arrival
    return delta.total_seconds() / 60.0


# ---------------------------------------------------------------------------
# Feature engineering helper
# ---------------------------------------------------------------------------

def build_feature_vector(
    distance_km: float,
    speed_kmh: float,
    delay_minutes: float = 0.0,
) -> np.ndarray:
    """
    Construct the [distance, speed, delay] feature row used by the ML model.
    Returns shape (1, 3).
    """
    return np.array([[distance_km, speed_kmh, delay_minutes]], dtype=float)
