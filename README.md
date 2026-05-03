# README.md

# Address Intelligence Library

A high-performance geospatial data pipeline designed to ingest, validate, enrich, and analyze large-scale US address datasets. The library transitions from raw address parsing to complex geographic enrichment by integrating US Census Bureau ACS data, HUD crosswalks, and spatial indexing via H3 hexagonal binning.

## Installation

The library requires Python 3.9+ and several scientific computing dependencies.

```bash
pip install pandas polars geopandas h3 pyarrow psutil requests shapely pyproj
```

## Quick Start

The following example demonstrates how to use the `EnvironmentManager` and `ZipCodeDataGenerator` to process address data.

```python
from main import EnvironmentManager, ZipCodeDataGenerator

# 1. Detect hardware capabilities and optimal batch settings
env = EnvironmentManager.get_processing_environment()
print(f"Using {env.parallel_processes} workers with batch size {env.batch_size}")

# 2. Initialize the generator
generator = ZipCodeDataGenerator()

# 3. Process mock data into a ZIP-grain CSV
mock_data = [{
    "zip_code": "64083",
    "state_abbrev": "MO",
    "state_name": "Missouri",
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
}]

generator.generate_zip_data(mock_data, "output_enrichment.csv")
```

## API Reference

### `core.schema`
- `AddressComponent`: Data container for the 15-field canonical schema.
- `validate_field(field_name: str, value: str) -> bool`: Validates a single component against reference data.

### `enrichment.census_engine`
- `ZipCodeDataGenerator.generate_zip_data(input_data: List[Dict], output_file: str)`: Orchestrates the full Census/HUD enrichment pipeline.
- `DemographicEnricher`: Performs ZCTA-level spatial joins for income and housing data.

### `enrichment.spatial_index`
- `H3Indexer.get_h3_index(lat: float, lon: float, resolution: int) -> str`: Returns H3 hexagonal cell ID.
- `ZCTAMapper`: Manages spatial join operations using GeoPandas.

### `processing.batch_orchestrator`
- `ParallelProcessor.process_file_parallel(input_path: str, output_path: str)`: Orchestrates chunked processing across CPU cores.
- `EnvironmentManager.get_optimal_batch_size() -> int`: Returns memory-safe batch size based on system telemetry.

### `io.adapters`
- `ExportManager.write_to_parquet(df: pd.DataFrame, path: str)`: Writes compressed Parquet.
- `ExportManager.write_to_delta(df: pd.DataFrame, path: str)`: Writes to Delta Lake format.

## Known Limitations
- **Memory Constraints**: While the library uses adaptive batching, processing datasets significantly larger than available RAM may still experience latency during the merge phase.
- **API Dependency**: Demographic enrichment relies on external US Census and HUD APIs; network availability is required.
- **US Only**: The validation logic and demographic crosswalks are strictly designed for United States address formats and ZIP codes.

## License
This project is licensed under the MIT License.