import pandas as pd
import pytest

# Import functions from the pipeline
from src.delivery_pipeline import (add_performance_metrics, drop_inconsistent_timestamps, 
                                   merge_sources, extract, add_fleet_info, add_fuel_costs,
                                   flatten_events_per_load, run_pipeline)


# ---------------------------------------------------------------------------
# add_performance_metrics
# ---------------------------------------------------------------------------

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
    assert not result.loc[0, "is_delayed_delivery"]


# ---------------------------------------------------------------------------
# drop_inconsistent_timestamps
# ---------------------------------------------------------------------------

def test_drop_inconsistent_timestamps_removes_invalid_rows():
    """Checks whether delivery before pickup is filtered correctly."""
    # 1. Arrange: A valid row (row 0) and an invalid row (row 1)
    dummy_data = pd.DataFrame({
        "load_id": [101, 102],
        "pickup_actual_datetime": [
            pd.Timestamp("2026-09-10 10:00:00"),
            pd.Timestamp("2026-09-10 10:00:00"),
        ],
        "delivery_actual_datetime": [
            pd.Timestamp("2026-09-10 12:00:00"),  # Valid: after pickup
            pd.Timestamp("2026-09-10 08:00:00"),  # Invalid: before pickup!
        ],
    })

    # 2. Act: Call pipeline-function
    result = drop_inconsistent_timestamps(dummy_data)

    # 3. Assert: Check, whether results are correct
    assert len(result) == 1
    assert result.iloc[0]["load_id"] == 101


# ---------------------------------------------------------------------------
# add_fleet_info
# ---------------------------------------------------------------------------

def test_add_fleet_info_merges_truck_and_trailer_columns():
    """Checks whether suffixes of collision-columns and fleet data are merged correctly."""
    # 1. Arrange: Create main dummy data and tables dict with overlapping column names ('status')
    dummy_data = pd.DataFrame({
        "load_id": [1],
        "truck_id": [20],
        "trailer_id": [200],
    })

    tables = {
        "trucks": pd.DataFrame({
            "truck_id": [20],
            "make": ["Volvo"],
            "status": ["Active"],  # collision-column 1
        }),
        "trailers": pd.DataFrame({
            "trailer_id": [200],
            "trailer_type": ["Dry Van"],
            "status": ["Maintenance"],  # collision-column 2
        })
    }

    # 2. Act: Call pipeline-function
    result = add_fleet_info(dummy_data, tables)

    # 3. Assert: Check whether truck and trailer info was added
    assert "make" in result.columns
    assert "trailer_type" in result.columns
    assert result.loc[0, "make"] == "Volvo"
    assert result.loc[0, "trailer_type"] == "Dry Van"

    # Check whether column collisions were handled with correct suffixes
    assert "status_truck" in result.columns
    assert "status_trailer" in result.columns
    assert result.loc[0, "status_truck"] == "Active"
    assert result.loc[0, "status_trailer"] == "Maintenance"


# ---------------------------------------------------------------------------
# add_fuel_costs
# ---------------------------------------------------------------------------

def test_add_fuel_costs_sums_purchases_per_trip():
    """Checks that multiple purchases per trip are summed into one row per load."""
    # 1. Arrange: three loads; purchases exist only for trip 11 (two) and trip 22 (one)
    # and an extra one for trip 99 that has no load
    df = pd.DataFrame({
        "load_id": [1, 2, 3],
        "trip_id": [11, 22, 33]
    })

    tables = {
        "fuel_purchases": pd.DataFrame({
            "fuel_purchase_id": [111, 222, 333, 444],
            "trip_id": [11, 11, 22, 99], # no entry for trip_id 33, trip 99 has no load
            "total_cost": [100.0, 50.0, 80.0, 60.0],
            "gallons": [30, 15, 25, 20]
        })
    }

    # 2. Act: Call pipeline-function
    result = add_fuel_costs(df, tables)

    # 3. Assert: trip 11 has two purchases -> costs 100 + 50, gallons 30 + 15, count 2
    by_trip = result.set_index("trip_id")
    assert len(result) == 3
    assert by_trip.loc[11, "fuel_cost"] == 150.0
    assert by_trip.loc[11, "fuel_gallons_purchased"] == 45.0
    assert by_trip.loc[11, "n_fuel_purchases"] == 2.0


def test_add_fuel_costs_leaves_nan_for_loads_without_purchases():
    """Checks that loads without any fuel purchase get NaN (not 0) in the fuel columns."""
    # 1. Arrange: three loads; purchases exist only for trip 11 (two) and trip 22 (one)
    df = pd.DataFrame({
        "load_id": [1, 2, 3],
        "trip_id": [11, 22, 33]
    })

    tables = {
        "fuel_purchases": pd.DataFrame({
            "fuel_purchase_id": [111, 222, 333],
            "trip_id": [11, 11, 22], # no entry for trip_id 33
            "total_cost": [100.0, 50.0, 80.0],
            "gallons": [30, 15, 25]
        })
    }

    # 2. Act: Call pipeline-function
    result = add_fuel_costs(df, tables)

    # 3. Assert: trip 33 has no purchase -> all fuel columns NaN, because 0 would suggest 
    # free fuel and inflate margins later
    by_trip = result.set_index("trip_id")
    assert pd.isna(by_trip.loc[33, "fuel_cost"])
    assert pd.isna(by_trip.loc[33, "fuel_gallons_purchased"])
    assert pd.isna(by_trip.loc[33, "n_fuel_purchases"])


def test_add_fuel_costs_raises_if_columns_already_exist():
    """Checks that a ValueError is raised if the load table already has a fuel_cost column."""
    # 1. Arrange: load table that already contains 'fuel_cost'
    df = pd.DataFrame({
            "load_id": [1, 2, 3],
            "trip_id": [11, 22, 33],
            "fuel_cost": [111.0, 222.0, 333.0]
        })

    tables = {
        "fuel_purchases": pd.DataFrame({
            "fuel_purchase_id": [111, 222, 333],
            "trip_id": [11, 11, 22], 
            "total_cost": [100.0, 50.0, 80.0],
            "gallons": [30, 15, 25]
        })
    }

    # 2. Act + 3. Assert: the call itself must fail
    with pytest.raises(ValueError, match="already exist"):
        add_fuel_costs(df, tables)


# ---------------------------------------------------------------------------
# extract
# ---------------------------------------------------------------------------

def test_extract_raises_file_not_found_when_file_missing(tmp_path):
    """Checks that extract raises FileNotFoundError if expected CSVs do not exist."""
    # Create only 1 file; 'trips.csv' and 'delivery_events.csv' are missing
    pd.DataFrame({"load_id": [1]}).to_csv(tmp_path / "loads.csv", index=False)

    with pytest.raises(FileNotFoundError):
        extract(tmp_path)


def test_extract_includes_routes_when_flag_is_true(tmp_path):
    """Checks that the routes table is loaded when include_routes=True"""
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


def test_extract_includes_fleet_when_flag_is_true(tmp_path):
    """Checks that the trucks and trailers tables are loaded when include_fleet=True."""
    # 1. Arrange: Write dummy CSVs into a temporary directory
    pd.DataFrame({"load_id": [1], "route_id": [10]}).to_csv(tmp_path / "loads.csv", index=False)
    pd.DataFrame({"load_id": [1], "trip_id": [100], "truck_id": [20], "trailer_id": [200]}).to_csv(tmp_path / "trips.csv", index=False)
    pd.DataFrame({"trip_id": [100]}).to_csv(tmp_path / "delivery_events.csv", index=False)
    pd.DataFrame({"route_id": [10]}).to_csv(tmp_path / "routes.csv", index=False)
    pd.DataFrame({"truck_id": [20]}).to_csv(tmp_path / "trucks.csv", index=False)
    pd.DataFrame({"trailer_id": [200]}).to_csv(tmp_path / "trailers.csv", index=False)

    # 2. Act: Call pipeline-function
    result = extract(tmp_path, include_fleet=True)

    # 3. Assert: Check, whether results are correct
    assert "trucks" in result
    assert "trailers" in result
    assert "trips" in result
    assert "delivery_events" in result


def test_extract_excludes_fleet_when_flag_is_false(tmp_path):
    """Checks that the trucks and trailers tables are not loaded when include_fleet=False."""
    # 1. Arrange: Write dummy CSVs into a temporary directory
    pd.DataFrame({"load_id": [1], "route_id": [10]}).to_csv(tmp_path / "loads.csv", index=False)
    pd.DataFrame({"load_id": [1], "trip_id": [100], "truck_id": [20], "trailer_id": [200]}).to_csv(tmp_path / "trips.csv", index=False)
    pd.DataFrame({"trip_id": [100]}).to_csv(tmp_path / "delivery_events.csv", index=False)
    pd.DataFrame({"route_id": [10]}).to_csv(tmp_path / "routes.csv", index=False)
    pd.DataFrame({"truck_id": [20]}).to_csv(tmp_path / "trucks.csv", index=False)
    pd.DataFrame({"trailer_id": [200]}).to_csv(tmp_path / "trailers.csv", index=False)

    # 2. Act: Call pipeline-function
    result = extract(tmp_path, include_fleet=False)

    # 3. Assert: Check, whether results are correct
    assert "trucks" not in result
    assert "trailers" not in result
    assert "trips" in result
    assert "delivery_events" in result


def test_extract_includes_fuel_purchases_when_flag_is_true(tmp_path):
    """Checks that fuel purchase table is loaded when include_costs=True."""
    # 1. Arrange: Write dummy CSVs into a temporary directory
    pd.DataFrame({"load_id": [1], "route_id": [10]}).to_csv(tmp_path / "loads.csv", index=False)
    pd.DataFrame({"load_id": [1], "trip_id": [100]}).to_csv(tmp_path / "trips.csv", index=False)
    pd.DataFrame({"trip_id": [100]}).to_csv(tmp_path / "delivery_events.csv", index=False)
    pd.DataFrame({"route_id": [10]}).to_csv(tmp_path / "routes.csv", index=False)
    pd.DataFrame({"fuel_purchase_id": [2], "trip_id": [100]}).to_csv(tmp_path / "fuel_purchases.csv", index=False)

    # 2. Act: Call pipeline-function
    result = extract(tmp_path, include_costs=True)

    # 3. Assert: Check, whether results are correct
    assert "loads" in result
    assert "trips" in result
    assert "delivery_events" in result
    assert "routes" in result
    assert "fuel_purchases" in result


def test_extract_excludes_fuel_purchases_when_flag_is_false(tmp_path):
    """Checks that fuel purchase table is not loaded when include_costs=False."""
    # 1. Arrange: Write dummy CSVs into a temporary directory
    pd.DataFrame({"load_id": [1], "route_id": [10]}).to_csv(tmp_path / "loads.csv", index=False)
    pd.DataFrame({"load_id": [1], "trip_id": [100]}).to_csv(tmp_path / "trips.csv", index=False)
    pd.DataFrame({"trip_id": [100]}).to_csv(tmp_path / "delivery_events.csv", index=False)
    pd.DataFrame({"route_id": [10]}).to_csv(tmp_path / "routes.csv", index=False)
    pd.DataFrame({"fuel_purchase_id": [2], "trip_id": [100]}).to_csv(tmp_path / "fuel_purchases.csv", index=False)

    # 2. Act: Call pipeline-function
    result = extract(tmp_path, include_costs=False)

    # 3. Assert: Check, whether results are correct
    assert "loads" in result
    assert "trips" in result
    assert "delivery_events" in result
    assert "routes" in result
    assert "fuel_purchases" not in result


# ---------------------------------------------------------------------------
# transform
# ---------------------------------------------------------------------------

def test_flatten_events_per_load_pivots_correctly():
    """Checks that multiple event rows are correctly flattened to 1 row per load_id."""
    dummy_merged = pd.DataFrame({
        "load_id_x": [1, 1],
        "load_id_y": [1, 1],
        "event_type": ["Pickup", "Delivery"],
        "scheduled_datetime": ["2026-09-10 10:00:00", "2026-09-10 12:00:00"],
        "actual_datetime": ["2026-09-10 10:05:00", "2026-09-10 12:10:00"],
        "facility_id": ["FAC1", "FAC2"],
        "detention_minutes": [0, 15],
        "on_time_flag": [True, True],
        "location_city": ["CityA", "CityB"],
        "location_state": ["NY", "NJ"],
        "event_id": [10, 11]
    })

    flat = flatten_events_per_load(dummy_merged)

    assert len(flat) == 1
    assert "pickup_scheduled_datetime" in flat.columns
    assert "delivery_scheduled_datetime" in flat.columns


# ---------------------------------------------------------------------------
# merge_sources
# ---------------------------------------------------------------------------


def test_merge_sources_includes_routes_when_flag_is_true():
    """Checks that route columns are merged when include_routes=True."""
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


# ---------------------------------------------------------------------------
# end-to-end
# ---------------------------------------------------------------------------

def test_run_pipeline_executes_end_to_end(tmp_path):
    """Checks full pipeline execution and file creation."""
    # Create mini-standard data in tmp_path
    pd.DataFrame({"load_id": [1], "route_id": [10]}).to_csv(tmp_path / "loads.csv", index=False)
    pd.DataFrame({"load_id": [1], "trip_id": [100]}).to_csv(tmp_path / "trips.csv", index=False)
    pd.DataFrame({
        "trip_id": [100, 100],
        "event_id": [1, 2],
        "event_type": ["Pickup", "Delivery"],
        "scheduled_datetime": ["2026-09-10 10:00:00", "2026-09-10 12:00:00"],
        "actual_datetime": ["2026-09-10 10:00:00", "2026-09-10 12:00:00"],
        "facility_id": ["F1", "F2"],
        "detention_minutes": [0, 0],
        "on_time_flag": [True, True],
        "location_city": ["A", "B"],
        "location_state": ["NY", "NJ"]
    }).to_csv(tmp_path / "delivery_events.csv", index=False)
    pd.DataFrame({"route_id": [10]}).to_csv(tmp_path / "routes.csv", index=False)

    out_file = tmp_path / "output.csv"
    res = run_pipeline(raw_dir=tmp_path, output_path=out_file, include_routes=True)

    assert out_file.exists()
    assert len(res) == 1


def test_run_pipeline_executes_end_to_end_with_flags(tmp_path):
    """Checks full pipeline run with routes, fleet and fuel costs enabled."""
    # Create mini-standard data in tmp_path
    pd.DataFrame({"load_id": [1], "route_id": [10]}).to_csv(tmp_path / "loads.csv", index=False)
    pd.DataFrame({
        "load_id": [1], 
        "trip_id": [100],
        "truck_id": [20],
        "trailer_id": [200]
    }).to_csv(tmp_path / "trips.csv", index=False)
    pd.DataFrame({
        "trip_id": [100, 100],
        "event_id": [1, 2],
        "event_type": ["Pickup", "Delivery"],
        "scheduled_datetime": ["2026-09-10 10:00:00", "2026-09-10 12:00:00"],
        "actual_datetime": ["2026-09-10 10:00:00", "2026-09-10 12:00:00"],
        "facility_id": ["F1", "F2"],
        "detention_minutes": [0, 0],
        "on_time_flag": [True, True],
        "location_city": ["A", "B"],
        "location_state": ["NY", "NJ"]
    }).to_csv(tmp_path / "delivery_events.csv", index=False)
    pd.DataFrame({"route_id": [10], "origin_city": ["Hamburg"]}).to_csv(tmp_path / "routes.csv", index=False)
    pd.DataFrame({"truck_id": [20], "make": ["Volvo"]}).to_csv(tmp_path / "trucks.csv", index=False)
    pd.DataFrame({"trailer_id": [200], "trailer_type": ["Dry Van"]}).to_csv(tmp_path / "trailers.csv", index=False)
    pd.DataFrame({
        "fuel_purchase_id": [1, 2], 
        "trip_id": [100, 100],
        "total_cost": [100.0, 50.0],
        "gallons": [30.0, 15.0]
    }).to_csv(tmp_path / "fuel_purchases.csv", index=False)
    
    
    out_file = tmp_path / "output.csv"
    res = run_pipeline(
        raw_dir=tmp_path, 
        output_path=out_file, 
        include_routes=True,
        include_fleet=True,
        include_costs=True)

    assert out_file.exists()
    assert len(res) == 1
    assert res.loc[0, "origin_city"] == "Hamburg"
    assert res.loc[0, "make"] == "Volvo"
    assert res.loc[0, "fuel_cost"] == 150.0
    assert res.loc[0, "n_fuel_purchases"] == 2.0