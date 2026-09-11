import pandas as pd
import pytest

# Import functions from the pipeline
from src.delivery_pipeline import add_performance_metrics, drop_inconsistent_timestamps


def test_add_performance_metrics_calculates_correctly():
    """Checks whether duration and delay (in hours) are calculated correctly."""
    # 1. Arrange: Prepare test data (1 delivery, 2-hour duration, 1-hour delay)
    dummy_data = pd.DataFrame({
        "pickup_actual_datetime": [pd.Timestamp("2026-09-10 10:00:00")],
        "delivery_scheduled_datetime": [pd.Timestamp("2026-09-10 11:00:00")],
        "delivery_actual_datetime": [pd.Timestamp("2026-09-10 12:00:00")],
    })

    # 2. Act: Call pipeline-function
    result = add_performance_metrics(dummy_data)

    # 3. Assert: Check, whether results are correct
    assert result.loc[0, "delivery_duration_hours"] == 2.0
    assert result.loc[0, "delivery_delay_hours"] == 1.0
    assert result.loc[0, "is_delayed_delivery"]


def test_drop_inconsistent_timestamps_removes_invalid_rows():
    """Checks whether delivery before pickup is filtered correctly."""
    # 1. Arrange: A valid row (row 0) and an invalide row (row 1)
    dummy_data = pd.DataFrame({
        "load_id": [101, 102],
        "pickup_actual_datetime": [
            pd.Timestamp("2026-09-10 10:00:00"),
            pd.Timestamp("2026-09-10 10:00:00"),
        ],
        "delivery_actual_datetime": [
            pd.Timestamp("2026-09-10 12:00:00"),  # Valid: after pickup
            pd.Timestamp("2026-09-10 08:00:00"),  # Invalide: before pickup!
        ],
    })

    # 2. Act: Call pipeline-function
    result = drop_inconsistent_timestamps(dummy_data)

    # 3. Assert: Check, whether results are correct
    assert len(result) == 1
    assert result.iloc[0]["load_id"] == 101


def test_add_performance_metrics_handles_on_time():
    """Checks, whether punctual deliveries have is_delayed_delivery = False."""
    # 1. Arrange: A pickup datetime (actual) and two delivery datetimes (scheduled and
    # actual)
    dummy_data = pd.DataFrame({
        "pickup_actual_datetime": [pd.Timestamp("2026-09-10 10:00:00")],
        "delivery_scheduled_datetime": [pd.Timestamp("2026-09-10 12:00:00")],
        "delivery_actual_datetime": [pd.Timestamp("2026-09-10 11:30:00")],
    })

    # 2. Act: Call pipeline-function
    result = add_performance_metrics(dummy_data)

    # 3. Assert: Check, whether results are correct
    assert result.loc[0, "delivery_delay_hours"] == -0.5
    assert result.loc[0, "delivery_delay_hours"] < 0.0
    assert result.loc[0, "is_delayed_delivery"] == False