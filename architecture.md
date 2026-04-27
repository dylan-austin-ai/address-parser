## Overview
The Address Intelligence Library is a Python-based package designed to handle address data normalization, standardization, and validation. It provides functions for parsing, validating, and correcting addresses based on the canonical 15-field address schema derived from US DOT National Address Database (NAD v17) and USPS Pub 28. The library includes reference data modules, string normalization functions, ZIP code validation, and an ETL pipeline for processing large datasets.

## Components
- **address_reference.py** — Contains all reference data including state codes, directional references, USPS street type references, and city name correction dictionaries.
- **normalization_functions.py** — Includes string normalization functions such as `clean_string`, `clean_standardize_zip`, and `clean_state`.
- **city_normalization_pipeline.py** — Orchestrates the city name standardization pipeline with multiple stages of corrections.
- **address_component_normalization.py** — Handles the detection and extraction of address components like directionals, street types, and unit numbers.
- **nad_etl.py** — Contains the ETL pipeline for processing NAD data, including chunk creation, transformation, and saving to parquet files.
- **memory_management.py** — Manages memory and process execution using `ProcessPoolExecutor` and garbage collection.

## Data Flow
1. Input address data is raw or semi-parsed string-based.
2. Reference data is loaded from `address_reference.py`.
3. Address strings undergo normalization using functions in `normalization_functions.py`.
4. City names are corrected through the pipeline defined in `city_normalization_pipeline.py`.
5. Address components are detected and extracted by `address_component_normalization.py`.
6. ETL pipeline processes NAD data in chunks, applying transformations from `nad_etl.py`.
7. Cleaned address data is saved to Parquet files for further processing or analysis.

## Dependencies
| Name | Version Pin | Purpose |
|------|-------------|---------|
| Polars | 0.14.13     | Data manipulation and analysis in a memory-efficient way. |
| tqdm   | 4.64.0      | Provides progress tracking for time-consuming tasks. |
| ast    | -           | Built-in Python library for evaluating strings containing Python expressions. |

## ADR
None