## Overview
The Address Intelligence Library is a high-performance geospatial data pipeline designed to ingest, validate, enrich, and analyze large-scale US address datasets. The system transitions from raw address parsing to complex geographic enrichment by integrating US Census Bureau ACS data, HUD crosswalks, and spatial indexing via H3 hexagonal binning. It is engineered for massive scale, utilizing parallel chunk processing and adaptive resource management to handle datasets exceeding 80 million records.

## Components
* **Address Engine**: Core logic for parsing and validating addresses against USPS and NAD standards.
* **Census & Demographic Module**: Orchestrates fetching and merging Census ACS and HUD crosswalk data for ZIP-level enrichment.
* **Spatial Intelligence Module**: Handles H3 hexagonal binning, ZCTA spatial joins using GeoPandas, and geodesic distance calculations.
* **Batch Processor**: A high-throughput execution engine using multiprocessing to handle large-scale ETL tasks.
* **Environment Manager**: Detects hardware capabilities (CPU/GPU) to adaptively configure batch sizes and processing modes.
* **Export Adapter**: Manages multi-format persistence including Parquet, SQLite, Delta tables, and CSV.

## Data Flow
1. **Ingestion & Environment Setup**: The system detects available system memory and CPU cores via `EnvironmentManager` to set optimal batch constraints.
2. **Address Validation**: Raw address strings are parsed into the 15-field canonical schema and validated against reference dictionaries.
3. **Geospatial Linking**: Validated coordinates are mapped to H3 hexagonal cells and ZCTA polygons via spatial joins.
4. **Demographic Enrichment**: The system fetches demographic variables (income, housing, population) from the Census API and joins them with address records via ZIP codes.
5. **Parallel Processing**: Large datasets are partitioned into chunks; `ProcessPoolExecutor` distributes these chunks across CPU cores for transformation.
6. **Persistence**: Enriched datasets are written to optimized formats (Parquet/Delta) for downstream BI or training consumption.

## Dependencies
| Name | Version Pin | Purpose |
|---|---|---|
| pandas | ^2.0.0 | DataFrame manipulation and Census data processing |
| polars | ^0.20.0 | High-performance lazy/streaming ETL for large datasets |
| geopandas | ^0.14.0 | Spatial joins between coordinates and ZCTA boundaries |
| h3 | ^4.0.0 | Hexagonal hierarchical spatial indexing |
| pyarrow | ^14.0.0 | Parquet file operations and data interoperability |
| psutil | ^5.9.0 | System resource (RAM/CPU) monitoring for adaptive scaling |
| requests | ^2.31.0 | Fetching data from Census and HUD APIs |
| shapely | ^2.0.0 | Geometric operations for spatial intersections |
| pyproj | ^3.6.0 | Geodesic distance calculations |

## ADR
**ADR 001: Adaptive Batch Sizing**
To prevent Out-Of-Memory (OOM) errors during massive ETL runs, the system will not use hardcoded batch sizes. Instead, it will use `psutil` to calculate a dynamic batch size based on 20% of available system memory, clamped within a safe range [100, 10000].

**ADR 002: Parallel Processing Strategy**
Given the CPU-bound nature of spatial joins and string parsing, the system will utilize `ProcessPoolExecutor` with `cpu_count - 1` workers. To prevent memory exhaustion during the merge phase, workers will write temporary Parquet files which are lazily combined.