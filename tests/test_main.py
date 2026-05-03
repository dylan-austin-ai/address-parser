import pytest
import os
import math
import csv
from main import EnvironmentManager, EnvironmentConfig, ZipCodeDataGenerator

# --- EnvironmentManager Tests ---

def test_environment_manager_get_optimal_batch_size_bounds():
    """Test that optimal batch size is always within the clamped range [100, 10000]."""
    batch_size = EnvironmentManager.get_optimal_batch_size()
    assert 100 <= batch_size <= 10000

def test_environment_manager_get_processing_environment_type():
    """Test that the environment config returns expected structure and defaults."""
    config = EnvironmentManager.get_processing_environment()
    assert isinstance(config, EnvironmentConfig)
    assert config.device in ["cpu", "cuda"]
    assert config.batch_size >= 100
    assert config.memory_limit > 0

def test_environment_manager_get_environment_summary_keys():
    """Test that environment summary contains all required descriptive keys."""
    summary = EnvironmentManager.get_environment_summary()
    expected_keys = {"environment_type", "configuration", "system_info", "optimal_batch_size", "validation_status"}
    assert expected_keys.issubset(summary.keys())
    assert isinstance(summary["configuration"], dict)
    assert isinstance(summary["system_info"], dict)

# --- ZipCodeDataGenerator Tests ---

@pytest.fixture
def generator():
    return ZipCodeDataGenerator()

@pytest.fixture
def temp_csv(tmp_path):
    return os.path.join(tmp_path, "test_output.csv")

def test_zip_code_data_generator_clean_text(generator):
    """Test text cleaning logic (lowercase, whitespace collapse)."""
    assert generator._clean_text("  HELLO   WORLD  ") == "hello world"
    assert generator._clean_text("NEW\nLINE") == "new line"
    assert generator._clean_text("  ") == ""
    assert generator._clean_text(None) == ""

def test_zip_code_data_generator_determine_zip_type(generator):
    """Test classification of ZIP types (Military, PO Box, Standard)."""
    # Military: starts with 096
    assert generator._determine_zip_type(100, "09612") == "Military"
    # PO Box: population <= 0
    assert generator._determine_zip_type(0, "12345") == "PO Box"
    assert generator._determine_zip_type(-5, "12345") == "PO Box"
    # Standard: has housing units (population > 0)
    assert generator._determine_zip_type(500, "12345") == "Standard"

def test_zip_code_data_generator_add_geographic_indicators(generator):
    """Test urbanization classification based on population density."""
    # urban_core: >= 3000
    assert generator._add_geographic_indicators(3500.0) == "urban_core"
    # urban_fringe: >= 1000
    assert generator._add_geographic_indicators(1500.0) == "urban_fringe"
    # suburban: >= 500
    assert generator._add_geographic_indicators(600.0) == "suburban"
    # rural: < 500
    assert generator._add_geographic_indicators(100.0) == "rural"
    # Edge case: exactly 500
    assert generator._add_geographic_indicators(500.0) == "suburban"

def test_zip_code_data_generator_calculate_derived_fields(generator):
    """Test housing unit totals, percentages, and density calculations."""
    row = {
        "owner_occupied_units": "800",
        "renter_occupied_units": "200",
        "population": 1000,
        "land_area_sqmi": 2.0
    }
    result = generator._calculate_derived_fields(row)
    
    assert result["total_housing_units"] == 1000.0
    assert result["owner_occupied_pct"] == 80.0  # (800/1000)*100
    assert result["population_density"] == 500.0 # 1000/2

    # Edge case: zero total housing
    row_zero = {"owner_occupied_units": 0, "renter_occupied_units": 0, "population": 0, "land_area_sqmi": 0}
    result_zero = generator._calculate_derived_fields(row_zero)
    assert result_zero["total_housing_units"] == 0.0
    assert result_zero["owner_occupied_pct"] == 0.0
    assert result_zero["population_density"] == 0.0

def test_zip_code_data_generator_generate_zip_data_happy_path(generator, temp_csv):
    """Test the full pipeline execution and CSV writing."""
    mock_input = [
        {
            "zip_code": "64083",
            "state_abbrev": "MO",
            "state_name": "Missouri",
            "county": "Jackson",
            "county_fips": "29095",
            "population": 25000,
            "land_area_sqmi": 45.5,
            "owner_occupied_units": 8000,
            "renter_occupied_units": 2000,
            "median_income": 65000.0,
            "median_home_value": 250000.0,
            "cbsa": "12345",
            "cbsa_type": "Metropolitan",
            "latitude": 39.0997,
            "longitude": -94.5786
        },
        {
            "zip_code": "9",  # Testing zero-fill to 5 digits
            "state_abbrev": "CA",
            "state_name": "California",
            "population": 0,
            "land_area_sqmi": 10.0
        }
    ]
    
    generator.generate_zip_data(mock_input, temp_csv)
    
    assert os.path.exists(temp_csv)
    with open(temp_csv, mode='r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    assert len(rows) == 2
    
    # Check first row (Missouri)
    assert rows[0]["zip_code"] == "64083"
    assert rows[0]["state_abbrev"] == "MO"
    assert rows[0]["region"] == "Midwest"
    assert float(rows[0]["owner_occupied_pct"]) == 80.0
    assert rows[0]["zip_type"] == "Standard"
    
    # Check second row (California zero-padded + PO Box)
    assert rows[1]["zip_code"] == "00009"
    assert rows[1]["state_abbrev"] == "CA"
    assert rows[1]["zip_type"] == "PO Box"

def test_zip_code_data_generator_error_handling(generator, temp_csv):
    """Test that the generator handles malformed input rows gracefully by skipping them."""
    mock_input = [
        {
            "zip_code": "64083",
            "state_abbrev": "MO",
            "population": 10,
            "land_area_sqmi": 1.0
        },
        {
            "zip_code": "BAD",
            "state_abbrev": "INVALID_STATE", # This might cause key errors in some implementations
            "population": "not_a_number" 
        }
    ]
    
    # Should not raise exception, should just log/skip
    generator.generate_zip_data(mock_input, temp_csv)
    
    with open(temp_csv, mode='r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Only the first valid row should be in the output
    assert len(rows) == 1
    assert rows[0]["zip_code"] == "64083"

def test_zip_code_data_generator_iso_and_region_mapping(generator, temp_csv):
    """Verify FIPS and Region mapping logic from the hardcoded dicts."""
    mock_input = [
        {"zip_code": "10001", "state_abbrev": "NY", "population": 100}, # Northeast
        {"zip_code": "30301", "state_abbrev": "GA", "population": 100}, # South
        {"zip_code": "90001", "state_abbrev": "CA", "population": 100}  # West
    ]
    
    generator.generate_zip_data(mock_input, temp_csv)
    
    with open(temp_csv, mode='r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    # NY mapping
    assert rows[0]["region"] == "Northeast"
    assert rows[0]["iso_state_code"] == "36"
    
    # GA mapping
    assert rows[1]["region"] == "South"
    assert rows[1]["iso_state_code"] == "13"
    
    # CA mapping
    assert rows[2]["region"] == "West"
    assert rows[2]["iso_state_code"] == "06"