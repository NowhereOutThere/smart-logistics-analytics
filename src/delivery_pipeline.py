"""ETL pipeline for the delivery performance dataset.

Loads raw loads/trips/routes/delivery_events tables, merges and flattens
them to one row per load, computes delivery duration and delay metrics,
and writes the cleaned result to data/processed/.

Usage:
    python src/delivery_pipeline.py
"""

import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)
   
# __file__ is path of this file (src/delivery_pipeline.py).
# .parent -> src/, .parent.parent -> project-root. This ensures the paths are always correct, regardless of where the script or notebook is running.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "clean_delivery_performance.csv"

EVENT_COLS = [
    "event_id", "event_type", "facility_id", "scheduled_datetime",
    "actual_datetime", "detention_minutes", "on_time_flag",
    "location_city", "location_state",
]
PIVOT_VALUES = [c for c in EVENT_COLS if c not in ("event_id", "event_type")]


def run_pipeline(raw_dir: Path = RAW_DATA_DIR, output_path: Path = PROCESSED_DATA_PATH) -> pd.DataFrame:
    """Run the full extract -> transform -> load pipeline and return the result."""
    raw = extract(raw_dir)
    df = transform(raw)
    load(df, output_path)
    return df


# ---------------------------------------------------------------------------
# Extract
# ---------------------------------------------------------------------------

def extract(raw_dir: Path) -> dict[str, pd.DataFrame]:
    """Read the four raw source tables and log their shapes."""
    tables = {}
    for name in ["loads", "trips", "delivery_events", "routes"]:
        path = raw_dir / f"{name}.csv"
        if not path.exists():
            raise FileNotFoundError(f"Expected source file not found: {path}")
        tables[name] = pd.read_csv(path)
        logger.info("%s: loaded %s rows, %s columns", name, *tables[name].shape)
    return tables


# ---------------------------------------------------------------------------
# Transform
# ---------------------------------------------------------------------------

def transform(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Merge, flatten, and enrich the raw tables into one row per load."""
    merged = merge_sources(tables)
    flat = flatten_events_per_load(merged)
    with_metrics = add_performance_metrics(flat)
    clean = drop_inconsistent_timestamps(with_metrics)
    return clean


def merge_sources(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Join loads/routes/trips/delivery_events into one long table (1 row per event)."""
    df = (
        tables["loads"]
        .merge(tables["routes"], how="left", on="route_id")
        .merge(tables["trips"], how="left", on="load_id")
        .merge(tables["delivery_events"], how="left", on="trip_id")
    )
    df["scheduled_datetime"] = pd.to_datetime(df["scheduled_datetime"])
    df["actual_datetime"] = pd.to_datetime(df["actual_datetime"])
    logger.info("Merged table: %s rows, %s columns", *df.shape)
    return df


def flatten_events_per_load(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot pickup/delivery events into columns so each load is a single row."""
    df = df.rename(columns={"load_id_x": "load_id"}).drop(columns=["load_id_y"], errors="ignore")

    events_pivoted = df.pivot_table(
        index="load_id", columns="event_type", values=PIVOT_VALUES, aggfunc="first"
    )
    events_pivoted.columns = [
        f"{event_type.lower()}_{field}" for field, event_type in events_pivoted.columns
    ]
    events_pivoted = events_pivoted.reset_index()

    load_base_info = df.drop(columns=EVENT_COLS).groupby("load_id", as_index=False).first()
    flat = pd.merge(load_base_info, events_pivoted, on="load_id", how="left")

    assert flat["load_id"].is_unique, "Expected exactly one row per load_id after flattening"
    logger.info("Flattened to %s loads (from %s event rows)", len(flat), len(df))
    return flat


def add_performance_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute delivery duration (hours) and delay (hours) per load."""
    df = df.copy()
    df["delivery_duration_hours"] = (
        (df["delivery_actual_datetime"] - df["pickup_actual_datetime"]).dt.total_seconds() / 3600
    ).round(2)
    df["delivery_delay_hours"] = (
        (df["delivery_actual_datetime"] - df["delivery_scheduled_datetime"]).dt.total_seconds() / 3600
    ).round(2)
    df["is_delayed_delivery"] = df["delivery_delay_hours"] > 0
    return df


def drop_inconsistent_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Remove loads where the delivery timestamp is before the pickup timestamp.

    Filters on the raw timestamps (not the rounded delivery_duration_hours)
    to correctly catch edge cases where sub-second differences round to 0.0.
    """
    n_before = len(df)
    clean = df[df["delivery_actual_datetime"] >= df["pickup_actual_datetime"]].copy()
    n_removed = n_before - len(clean)
    logger.info(
        "Removed %d loads with inconsistent timestamps (%.2f%%)",
        n_removed, n_removed / n_before * 100 if n_before else 0,
    )
    return clean


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def load(df: pd.DataFrame, output_path: Path) -> None:
    """Write the cleaned dataset to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Saved cleaned data to %s (%s rows)", output_path, len(df))


if __name__ == "__main__":
    run_pipeline()