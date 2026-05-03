## Package Layout
```text
address_intelligence/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── schema.py
│   ├── address_reference.py
│   └── pre_processing_elements.py
├── enrichment/
│   ├── __init__.py
│   ├── census_engine.py
│   ├── spatial_index.py
│   └── risk_models.py
├── processing/
│   ├── __init__.py
│   ├── batch_orchestrator.py
│   └── environment_manager.py
├── io/
│   ├── __init__.py
│   ├── adapters.py
│   └── spatial_io.py
└── utils/
    ├── __init__.py
    └── geo_utils.py
```

## Module Responsibilities

**core**: Defines the canonical 15-field address schema and holds the immutable reference dictionaries for street suffixes, directionals, and city corrections derived from NAD/USPS.

**enrichment**: Contains the heavy-lifting logic for demographic augmentation, including Census API interaction, HUD crosswalk mapping, and H3-based spatial binning.

**processing**: Manages the execution lifecycle, including hardware-aware resource allocation and the parallel chunking logic used to process millions of rows without crashing the host system.

**io**: Provides a unified interface for reading from and writing to various file formats, ensuring that optimized storage like Parquet and Delta is used for large datasets while maintaining CSV compatibility.

**utils**: Houses low-level geometric helpers and coordinate transformation logic used across the library.

## Public API

### core.schema
- `class AddressComponent`: Data container for the 15-field canonical schema.
- `def validate_field(field_name: str, value: str) -> bool`: Validates a single component against reference data.

### enrichment.census_engine
- `class ZipCodeDataGenerator`: Generates 22-column ZIP grain tables.
    - `def generate_zip_data(output_file: str) -> None`: Orchestrates the full Census/HUD enrichment pipeline.
- `class DemographicEnricher`: Performs ZCTA-level spatial joins for income/housing data.

### enrichment.spatial_index
- `class H3Indexer`: Handles hexagonal binning.
    - `def get_h3_index(lat: float, lon: float, resolution: int) -> str`: Returns H3 cell ID.
- `class ZCTAMapper`: Manages spatial join operations using GeoPandas.

### processing.batch_orchestrator
- `class ParallelProcessor`: Manages multi-process execution.
    - `def process_file_parallel(input_path: str, output_path: str) -> None`: Orchestrates chunked processing.
- `class EnvironmentManager`: System telemetry.
    - `def get_optimal_batch_size() -> int`: Returns memory-safe batch size.

### io.adapters
- `class ExportManager`: Multi-format dispatcher.
    - `def write_to_parquet(df: pd.DataFrame, path: str) -> None`: Writes compressed Parquet.
    - `def write_to_delta(df: pd.DataFrame, path: str) -> None`: Writes to Delta Lake format.