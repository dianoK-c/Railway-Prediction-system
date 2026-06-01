"""
models/ml_model.py
------------------
Trains and persists a LinearRegression model to predict ETA (minutes)
from [distance_km, speed_kmh, current_delay_minutes].

Historical training data is synthetically generated to bootstrap the model
on first run.  Real operational data can be appended via `append_history()`.
"""

from __future__ import annotations

import os
import pickle
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_PATH = DATA_DIR / "eta_model.pkl"
SCALER_PATH = DATA_DIR / "scaler.pkl"
HISTORY_PATH = DATA_DIR / "history.csv"

DATA_DIR.mkdir(exist_ok=True)

# Column schema
FEATURE_COLS = ["distance_km", "speed_kmh", "delay_minutes"]
TARGET_COL = "actual_eta_minutes"


# ---------------------------------------------------------------------------
# Synthetic data generator (bootstraps the model when no real data exists)
# ---------------------------------------------------------------------------

def _generate_synthetic_data(n: int = 2000, seed: int = 42) -> pd.DataFrame:
    """
    Generate plausible train-journey records.

    Rules
    -----
    - Distance 2–300 km
    - Speed 30–200 km/h  (low for local, high for express)
    - Delay -5 to +30 min
    - Actual ETA ≈ physics ETA + small Gaussian noise + 0.4 × delay
    """
    rng = np.random.default_rng(seed)

    distance = rng.uniform(2, 300, n)
    speed = rng.uniform(30, 200, n)
    delay = rng.uniform(-5, 30, n)

    physics_eta = (distance / speed) * 60.0
    noise = rng.normal(0, 2, n)                 # ±2 min operational noise
    actual_eta = physics_eta + 0.4 * delay + noise
    actual_eta = np.clip(actual_eta, 1, None)   # ETA can't be negative

    return pd.DataFrame(
        {
            "distance_km": distance,
            "speed_kmh": speed,
            "delay_minutes": delay,
            TARGET_COL: actual_eta,
        }
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def train_model(force: bool = False) -> dict:
    """
    Train (or retrain) the ETA model and persist it to disk.

    Parameters
    ----------
    force : bool  – retrain even if a saved model already exists

    Returns
    -------
    dict  – training metrics  {mae, r2, n_samples}
    """
    # Load or generate training data
    if HISTORY_PATH.exists():
        df = pd.read_csv(HISTORY_PATH)
        # Ensure synthetic seed data is always included
        synthetic = _generate_synthetic_data()
        df = pd.concat([synthetic, df], ignore_index=True)
    else:
        df = _generate_synthetic_data()
        df.to_csv(HISTORY_PATH, index=False)

    X = df[FEATURE_COLS].values
    y = df[TARGET_COL].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Scale features
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # Train
    model = LinearRegression()
    model.fit(X_train_s, y_train)

    # Evaluate
    y_pred = model.predict(X_test_s)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Persist
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)

    return {"mae": round(mae, 2), "r2": round(r2, 4), "n_samples": len(df)}


def load_model() -> tuple[LinearRegression, StandardScaler]:
    """Load persisted model & scaler, training on first call."""
    if not MODEL_PATH.exists() or not SCALER_PATH.exists():
        train_model()
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
    return model, scaler


def predict_eta(
    distance_km: float,
    speed_kmh: float,
    delay_minutes: float = 0.0,
) -> float:
    """
    ML-predicted ETA in minutes.

    Parameters
    ----------
    distance_km    : float  – remaining distance
    speed_kmh      : float  – current speed
    delay_minutes  : float  – known cumulative delay so far

    Returns
    -------
    float  – predicted ETA in minutes (always ≥ 0)
    """
    model, scaler = load_model()
    X = np.array([[distance_km, speed_kmh, delay_minutes]], dtype=float)
    X_s = scaler.transform(X)
    eta = model.predict(X_s)[0]
    return max(0.0, float(eta))


def append_history(
    distance_km: float,
    speed_kmh: float,
    delay_minutes: float,
    actual_eta_minutes: float,
) -> None:
    """
    Append one completed journey record to the history CSV.
    Call `train_model(force=True)` afterwards to retrain with new data.
    """
    row = pd.DataFrame(
        [
            {
                "distance_km": distance_km,
                "speed_kmh": speed_kmh,
                "delay_minutes": delay_minutes,
                TARGET_COL: actual_eta_minutes,
            }
        ]
    )
    if HISTORY_PATH.exists():
        row.to_csv(HISTORY_PATH, mode="a", header=False, index=False)
    else:
        row.to_csv(HISTORY_PATH, index=False)
