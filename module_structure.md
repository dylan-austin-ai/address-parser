## Package Layout
```
address_intelligence/
├── address_reference.py
├── normalization_functions.py
├── city_normalization_pipeline.py
├── address_component_normalization.py
├── nad_etl.py
├── memory_management.py
└── __init__.py
```

## Module Responsibilities
- **address_reference.py** — Contains all reference data including state codes, directional references, USPS street type references, and city name correction dictionaries.
- **normalization_functions.py** — Provides core string normalization functions such as `clean_string`, `clean_standardize_zip`, and `clean_state`.
- **city_normalization_pipeline.py** — Orchestrates the complex process of standardizing city names through multiple steps of corrections.
- **address_component_normalization.py** — Handles the detection, extraction, and validation of address components like directionals, street types, and unit numbers.
- **nad_etl.py** — Manages the ETL pipeline for processing NAD data in chunks, applying necessary transformations and saving cleaned data to Parquet files.
- **memory_management.py** — Implements strategies for efficient memory usage and process execution, using tools like `ProcessPoolExecutor` and garbage collection.

## Public API
### address_reference.py
```python
state_codes: list
full_state_name_to_two_digit_state_code: dict
full_state_name_variations: dict
address_directionals: dict
list_of_address_directionals: set
bound_directionals_dict: dict
usps_st_posttyp: list
suffix_substring_dict: dict
complete_word_replacement_dict: dict
compound_word_corrections_dict: dict
multi_word_replacement_dict: dict
state_specific_replacements: dict
st_premod_replacements: dict
st_pretyp_replacements: dict
```

### normalization_functions.py
```python
clean_string(input_string) -> str
clean_standardize_zip(input) -> str
clean_state(state, state_codes) -> str
```

### city_normalization_pipeline.py
```python
city_name_word_suffix_correction(city_name, suffix_substring_dict) -> str
city_name_standardize_whole_words(city_name, complete_word_replacement_dict) -> str
city_name_fix_compound_words(city_name, compound_corrections_dict) -> str
city_name_fix_multiword_strings(city_name, multi_word_replacement_dict) -> str
state_specific_city_fixes(city_name, state_code, state_specific_replacements_dict) -> str
clean_standardize_city(input_city_name, input_state_code) -> str
```

### address_component_normalization.py
```python
move_directionals(st_name, ...) -> (st_name, st_predir, st_posdir)
move_street_type(st_name, usps_st_posttyp) -> (st_name, st_postyp)
move_unit_numbers(st_name) -> (st_name, secondary_address)
```

### nad_etl.py
```python
transform_column(col_name) -> pl.Expr
clean_addnum_pre_lazy(lazy_frame, ...) -> pl.LazyFrame
clean_addnum_suf_lazy(lazy_frame) -> pl.LazyFrame
clean_st_premod_lazy(lazy_frame, ...) -> pl.LazyFrame
clean_st_predir_lazy(lazy_frame) -> pl.LazyFrame
clean_st_pretyp_lazy(lazy_frame, st_pretyp_replacements) -> pl.LazyFrame
clean_st_name_lazy(lazy_frame, ...) -> pl.LazyFrame
clean_st_posdir_lazy(lazy_frame) -> pl.LazyFrame
clean_st_posmod_lazy(lazy_frame) -> pl.LazyFrame
calculate_optimal_batch_size(batch_size) -> int
create_lazy_chunks(file_path, chunk_size=1_000_000) -> generator[pl.LazyFrame]
process_nad_file(input_file, output_file, batch_size)
extract_address_data(nad_input_file, nad_output_file, batch_size=5_000_000, regenerate=False)
extract_address_elements_from_national_address_database(input_file, output_file, sample_only=False)
```

### memory_management.py
```python
setup_logging() -> logging.Logger