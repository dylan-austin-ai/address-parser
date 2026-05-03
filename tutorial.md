# Tutorial

By the end of this tutorial, you will have successfully built a high-performance geospatial enrichment pipeline that converts raw, unformatted ZIP code data into a structured, intelligence-rich dataset containing demographic metrics, urbanization levels, and standardized geographic indicators.

## Prerequisites

Ensure you have Python 3.9 or higher installed on your system. You will also need `psutil` installed to allow the library to perform hardware-aware resource management.

```bash
pip install psutil
```

## Step 1: Environment Detection and Resource Allocation

The Address Intelligence Library is designed for massive scale. Before processing, the `EnvironmentManager` analyzes your system's available RAM and CPU cores. It uses a non-static batch sizing strategy to prevent "Out-Of-Memory" (OOM) errors by allocating only 20% of available memory to the processing buffer.

Run the following command to simulate an environment check:

```python
from main import EnvironmentManager

# Detect hardware and calculate optimal batch size
env = EnvironmentManager.get_processing_environment()
summary = EnvironmentManager.get_environment_summary()

print(f"Detected Device: {env.device}")
print(f"Optimal Batch Size: {env.batch_size}")
print(f"System Summary: {summary['configuration']}")
```

**Expected Output:**
```text
Detected Device: cpu
Optimal Batch Size: 10000
System Summary: {'device': 'cpu', 'parallel_processes': 7, 'batch_size': 10000, 'memory_limit_gb': 15.4}
```
*(Note: Your actual batch size and processes will vary based on your local hardware.)*

## Step 2: Initializing the Data Generator

The `ZipCodeDataGenerator` serves as the orchestration engine for the enrichment pipeline. It handles text cleaning, ZIP type classification (Standard vs. Military), and calculates derived geographic indicators like population density.

First, prepare your raw input data. In a real-world scenario, this would be a large CSV or database export.

```python
from main import ZipCodeDataGenerator

generator = ZipCodeDataGenerator()

# Mock raw data representing uncleaned Census/HUD input
mock_input_data = [
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
    }
]

# Define the output destination
output_path = "enriched_zip_data.csv"

# Execute the enrichment pipeline
generator.generate_zip_data(mock_input_data, output_path)
print(f"Pipeline complete. File saved to {output_path}")
```

**Expected Output:**
```text
Pipeline complete. File saved to enriched_zip_data.csv
```

## Step 3: Validating Enriched Data

Once the pipeline completes, the library has calculated complex fields such as `owner_occupied_pct`, `urbanization_level`, and `population_density`. You can verify the transformation by reading the resulting CSV.

```python
import pandas as pd

# Load the enriched results
df = pd.read_csv("enriched_zip_data.csv")

# Display the transformed intelligence fields
print(df[["zip_code", "zip_type", "urbanization_level", "population_density", "owner_occupied_pct"]].to_string())
```

**Expected Output:**
```text
  zip_code zip_type urbanization_level  population_density  owner_occupied_pct
0    64083  Standard          suburban             549.451429            80.0
```

## Summary of Achievements

You have successfully navigated the full lifecycle of the Address Intelligence Library:
1. **Hardware Awareness**: Leveraged `psutil` to ensure the process scales to your specific machine without crashing.
2. **Data Ingestion**: Ingested raw demographic mappings.
3. **Geospatial Enrichment**: Transformed raw population and area numbers into meaningful `urbanization_level` classifications.
4. **Economic Analytics**: Derived homeownership percentages and density metrics ready for downstream BI consumption.