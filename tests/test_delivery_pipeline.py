import pandas as pd
import pytest

# Import functions from the pipeline
from src.delivery_pipeline import (add_performance_metrics, drop_inconsistent_timestamps, 
                                   merge_sources, extract)


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


def test_merge_sources_excludes_routes_when_flag_is_false():
    """Checks that routes columns are absent when include_routes=False."""
    # 1. Arrange: Four dummy tables (loads, trips, delivery_events, routes)
    tables = {
        "loads": pd.DataFrame({"load_id": [1], "route_id": [10]}),
        "trips": pd.DataFrame({"load_id": [1], "trip_id": [100]}),
        "delivery_events": pd.DataFrame({
            "trip_id": [100],
            "scheduled_datetime": [pd.Timestamp("2026-09-10 10:00:00")],
            "actual_datetime": [pd.Timestamp("2026-09-10 11:00:00")]}),
        "routes": pd.DataFrame({
            "route_id": [10], 
            "origin_city": ["Hamburg"],
        })
    }

    # 2. Act: Call pipeline-function
    result = merge_sources(tables, include_routes=False)

    # 3. Assert: Check, whether results are correct
    assert "origin_city" not in result.columns
    assert "load_id" in result.columns
    assert "trip_id" in result.columns
    assert "scheduled_datetime" in result.columns
    assert result.loc[0, "trip_id"] == 100



def test_merge_sources_includes_routes_when_flag_is_true():
    """Checks merge function"""
    # 1. Arrange: Four dummy tables (loads, trips, delivery_events, routes)
    tables = {
        "loads": pd.DataFrame({"load_id": [1], "route_id": [10]}),
        "trips": pd.DataFrame({"load_id": [1], "trip_id": [100]}),
        "delivery_events": pd.DataFrame({
            "trip_id": [100],
            "scheduled_datetime": [pd.Timestamp("2026-09-10 10:00:00")],
            "actual_datetime": [pd.Timestamp("2026-09-10 11:00:00")]}),
        "routes": pd.DataFrame({
            "route_id": [10], 
            "origin_city": ["Hamburg"],
        })
    }

    # 2. Act: Call pipeline-function
    result = merge_sources(tables, include_routes=True)

    # 3. Assert: Check, whether results are correct
    assert "origin_city" in result.columns
    assert "load_id" in result.columns
    assert "trip_id" in result.columns
    assert "scheduled_datetime" in result.columns
    assert result.loc[0, "origin_city"] == "Hamburg"
    assert result.loc[0, "trip_id"] == 100


def test_extract_excludes_routes_when_flag_is_false(tmp_path):
    """Checks that the routes table is not loaded when include_routes=False."""
    # 1. Arrange: Write dummy CSVs into a temporary directory
    pd.DataFrame({"load_id": [1], "route_id": [10]}).to_csv(tmp_path / "loads.csv", index=False)
    pd.DataFrame({"load_id": [1], "trip_id": [100]}).to_csv(tmp_path / "trips.csv", index=False)
    pd.DataFrame({"trip_id": [100]}).to_csv(tmp_path / "delivery_events.csv", index=False)
    pd.DataFrame({"route_id": [10]}).to_csv(tmp_path / "routes.csv", index=False)

    # 2. Act: Call pipeline-function
    result = extract(tmp_path, include_routes=False)

    # 3. Assert: Check, whether results are correct
    assert "routes" not in result
    assert "loads" in result
    assert "trips" in result
    assert "delivery_events" in result



def test_extract_includes_routes_when_flag_is_true(tmp_path):
    """Checks extract function"""
    # 1. Arrange: Write dummy CSVs into a temporary directory
    pd.DataFrame({"load_id": [1], "route_id": [10]}).to_csv(tmp_path / "loads.csv", index=False)
    pd.DataFrame({"load_id": [1], "trip_id": [100]}).to_csv(tmp_path / "trips.csv", index=False)
    pd.DataFrame({"trip_id": [100]}).to_csv(tmp_path / "delivery_events.csv", index=False)
    pd.DataFrame({"route_id": [10]}).to_csv(tmp_path / "routes.csv", index=False)

    # 2. Act: Call pipeline-function
    result = extract(tmp_path, include_routes=True)

    # 3. Assert: Check, whether results are correct
    assert "routes" in result
    assert "loads" in result
    assert "trips" in result
    assert "delivery_events" in result
