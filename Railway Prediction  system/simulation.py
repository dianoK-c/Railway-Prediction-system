"""
utils/simulation.py
-------------------
Generates a sequence of simulated train positions between two stations.
Used by the "Live Simulation" tab to mimic real-time location updates.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Generator


@dataclass
class TrainSnapshot:
    """A single point-in-time snapshot of a train's state."""
    step: int
    lat: float
    lon: float
    speed_kmh: float
    distance_remaining_km: float
    elapsed_minutes: float
    eta_minutes: float


def interpolate_position(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
    fraction: float,
) -> tuple[float, float]:
    """
    Linearly interpolate between two (lat, lon) pairs.
    `fraction` is in [0, 1].
    """
    lat = lat1 + (lat2 - lat1) * fraction
    lon = lon1 + (lon2 - lon1) * fraction
    return lat, lon


def simulate_journey(
    origin_lat: float, origin_lon: float,
    dest_lat: float, dest_lon: float,
    total_distance_km: float,
    avg_speed_kmh: float,
    n_steps: int = 20,
    speed_variance: float = 10.0,
    seed: int | None = None,
) -> list[TrainSnapshot]:
    """
    Return a list of `n_steps` TrainSnapshots from origin → destination.

    Parameters
    ----------
    total_distance_km  – great-circle distance between the two stations
    avg_speed_kmh      – mean operational speed
    n_steps            – number of simulation ticks
    speed_variance     – ±km/h random fluctuation per step
    """
    rng = random.Random(seed)
    snapshots: list[TrainSnapshot] = []
    elapsed = 0.0

    for step in range(n_steps + 1):
        fraction = step / n_steps
        lat, lon = interpolate_position(
            origin_lat, origin_lon, dest_lat, dest_lon, fraction
        )

        # Randomise speed slightly (acceleration / deceleration near stations)
        if fraction < 0.1 or fraction > 0.9:
            speed = avg_speed_kmh * 0.5          # slow near stations
        else:
            noise = rng.uniform(-speed_variance, speed_variance)
            speed = max(10.0, avg_speed_kmh + noise)

        distance_remaining = total_distance_km * (1 - fraction)
        eta = (distance_remaining / speed * 60.0) if speed > 0 else 0.0

        # Elapsed time since previous step
        if step > 0:
            prev_frac = (step - 1) / n_steps
            seg_dist = total_distance_km / n_steps
            elapsed += (seg_dist / speed) * 60.0   # minutes

        snapshots.append(
            TrainSnapshot(
                step=step,
                lat=lat,
                lon=lon,
                speed_kmh=round(speed, 1),
                distance_remaining_km=round(distance_remaining, 3),
                elapsed_minutes=round(elapsed, 2),
                eta_minutes=round(eta, 2),
            )
        )

    return snapshots
