# Address Intelligence Library — Phased Feature Brief

Reorganized from: `features_and_functions_brief.md`
Date: 2026-04-23

Each phase builds directly on the layer below it. Phase 1 must be stable before Phase 2 begins, etc. The canonical address component schema applies to all phases and is defined here first.

---

## Canonical Address Component Schema

All phases share this 15-field schema, derived from US DOT National Address Database (NAD v17) and USPS Pub 28.

| Field | Description | Example |
|---|---|---|
| `addnum_pre` | Address number prefix (e.g., mile marker) | TM, MM |
| `add_number` | Primary house/building number | 1208 |
| `addnum_suf` | Address number suffix (fractions/decimals) | 1/2, .5 |
| `st_premod` | Street pre-modifier | OLD, NEW, STATE |
| `st_predir` | Pre-directional | N, SW, NORTH |
| `st_pretyp` | Street pre-type | HIGHWAY, ROUTE, FM |
| `st_presep` | Pre-type separator | — |
| `st_name` | Street name | LAKECREST |
| `st_postyp` | Street post type (suffix) | ST, AVE, BLVD, CIR |
| `st_posdir` | Post-directional | NW, SE |
| `st_posmod` | Street post-modifier | NORTHBOUND, EXT |
| `secondary_address` | Unit/suite/floor/building | APT 3, UNIT A, FLOOR 2 |
| `post_city` | Mailing city name | RAYMORE |
| `state` | 2-letter state code | MO |
| `zip_code` | 5-digit ZIP code | 64083 |

**Derived field:**
- `full_address` — concatenation of all components into a single parseable string

---

## Companion Data Files

This brief fully specifies all code logic, algorithms, and function signatures. However, several sections in Phase 1 depend on large reference dictionaries whose entries were derived empirically from US DOT NAD v17 analysis and USPS Pub 28 — they cannot be reliably reconstructed from general knowledge.

**Sections that require companion data files are marked inline with `[DATA FILE REQUIRED]`.**

### Files to provide alongside this brief

| File | What it contains | Used in |
|---|---|---|
| `address_reference.py` | All 5 city correction dicts, `usps_st_posttyp`, `st_pretyp_replacements`, `st_premod_replacements`, state/directional refs | Sections 1.2, 1.7 |
| `pre_processing_nad_elements.py` | NAD column-specific blacklists: invalid values for `st_premod`, `st_posmod`, `st_predir` | Section 1.7 |

**Full paths (relative to `raw_files_to_scan/`):**
- `Articles/projects/address_parsing_neural_net/src/address/address_reference.py`
- `Articles/projects/address_parsing_neural_net/src/national_address_database/pre_processing_nad_elements.py`

### How to use

When starting a Phase 1 implementation session, provide both source files above as read-only context alongside this brief. The AI should copy dictionary contents verbatim into the new project's `address_reference.py` — not infer, invent, or reconstruct entries. The city correction dictionaries and state-specific entries in particular were derived from observed NAD data quality issues and cannot be approximated from general knowledge.

---

# PHASE 1 — Foundation
### Reference Data · String Normalization · Address Component Standardization

**Goal:** Build the complete normalization and reference data layer. Every later phase depends on these functions being correct and tested. Phase 1 produces no ML, no geocoding, no external API calls — only deterministic text processing.

**Deliverables:** A fully tested Python package with reference dictionaries, all normalization functions, the ZIP/state/city validation pipeline, and the NAD ETL pipeline that produces clean training data for Phase 2.

---

## 1.1 Address Component Schema & Data Model

- Define the 15-field canonical schema as dataclasses or typed dicts
- Define `full_address` assembly logic: `"{addno_full} {stnam_full} {secondary_address}, {post_city}, {state} {zip_code}"`
- Define `secondary_address` assembly: concatenate building + floor + unit + room + seat fields with labels

---

## 1.2 Reference Data Module

All reference data lives in a single module (`address_reference.py` pattern). This is the source of truth for all downstream normalization.

### State Reference
- `state_codes` — list of 51 valid 2-letter codes (DC included, territories excluded)
- `full_state_name_to_two_digit_state_code` — uppercase full name → 2-letter code (51 entries)
- `full_state_name_variations` — common abbreviation variants → 2-letter code:
  - 3-letter truncations (ALA→AL, ARK→AR, etc.)
  - 4-letter truncations (ALAB→AL, CONN→CT, etc.)
  - 5-letter truncations (ALABA→AL, CALIF→CA, etc.)
  - Directional permutations (N DAKOTA, NO DAKOTA, NORT DAKOTA, etc.)
  - State nicknames (BLUEGRASS STATE→KY, GOLDEN STATE→CA, LONE STAR STATE→TX, etc. — ~80 entries)
  - DC variants (WASH D C, WASHINGTON DC, WASHINGTON D C)

### Directional Reference
- `address_directionals` — abbreviation → full name (16 entries):
  - Cardinal: N→NORTH, S→SOUTH, E→EAST, W→WEST
  - Intercardinal: NW→NORTHWEST, SW→SOUTHWEST, NE→NORTHEAST, SE→SOUTHEAST
  - Secondary intercardinal: NNW, NNE, SSW, SSE, WNW, WSW, ENE, ESE
- `list_of_address_directionals` — flat list of all valid directional full names
- `bound_directionals_dict` — NB→NORTHBOUND, SB→SOUTHBOUND, EB→EASTBOUND, WB→WESTBOUND

### USPS Street Type Reference

> **[DATA FILE REQUIRED: `address_reference.py`]** Copy `usps_st_posttyp` verbatim. The list follows USPS Pub 28 exactly (~200 approved suffixes); do not reconstruct from general knowledge.

- `usps_st_posttyp` — full USPS Pub 28 list of approved street suffixes (~200 entries)
  Used to detect and extract post types embedded in street names

### City Name Correction Dictionaries (5 dictionaries)

> **[DATA FILE REQUIRED: `address_reference.py`]** All 5 dictionaries below must be copied verbatim. Combined size is ~1,000+ entries. `complete_word_replacement_dict` and `state_specific_replacements` are the largest and most domain-specific — they encode NAD data quality patterns that cannot be inferred. Do not generate placeholder entries; an incomplete dict will silently produce wrong normalization.

- `suffix_substring_dict` — city suffix typo corrections (12 entries):
  - `'VLE'`→`'VILLE'`, `'TN'`→`'TON'`, `'BG'`→`'BURG'`, `'CHESTR'`→`'CHESTER'`, `'FLD'`→`'FIELD'`, `'LND'`→`'LAND'`, etc.
- `complete_word_replacement_dict` — word-token standardizations (~500+ entries):
  - Abbreviations: `'GRN'`→`'GREEN'`, `'HGTS'`→`'HEIGHTS'`, `'MTN'`→`'MOUNTAIN'`
  - Misspellings: `'BLMNGTON'`→`'BLOOMINGTON'`, `'CHARLOTTEVLE'`→`'CHARLOTTESVILLE'`
  - Military base codes: `'AFB'`→`'AIR FORCE BASE'`, `'NAS'`→`'NAVAL AIR STATION'`
  - Directionals at word level: `'NW'`→`'NORTHWEST'`, etc.
- `compound_word_corrections_dict` — incorrectly split compound names (9 entries):
  - `'BLOOM FIELD'`→`'BLOOMFIELD'`, `'RIVER SIDE'`→`'RIVERSIDE'`, `'WOOD LAND'`→`'WOODLAND'`
- `multi_word_replacement_dict` — full multi-word phrase corrections (~150+ entries):
  - Hyphenation: `'WINSTON SALEM'`→`'WINSTON-SALEM'`, `'FUQUAY VARINA'`→`'FUQUAY-VARINA'`
  - Spacing: `'GREEN ACRES'`→`'GREENACRES'`, `'COCONUTCREEK'`→`'COCONUT CREEK'`
  - Military: `'FT SM HOUSTON'`→`'FORT SAM HOUSTON'`
- `state_specific_replacements` — nested by state code, all 50 states (~300+ total entries):
  - Per-state dicts of `{'wrong_city': 'correct_city'}` for known NAD data quality issues
  - Examples: FL `'NEW POINT RICHEY'`→`'NEW PORT RICHEY'`, PA `'KING OF PRUSSA'`→`'KING OF PRUSSIA'`, TX `'ROSE CITY'`→`'ROYSE CITY'`

### Street Component Correction Dictionaries

> **[DATA FILE REQUIRED: `address_reference.py`]** Copy `st_premod_replacements` and `st_pretyp_replacements` verbatim. `st_pretyp_replacements` covers ~200+ abbreviation forms including BIA routes, county roads, state routes, and farm roads that are not recoverable from general knowledge.

- `st_premod_replacements` — pre-modifier normalizations (e.g., `'I'`→`'INTERSTATE'`, `'NYS'`→`'NEW YORK STATE'`)
- `st_pretyp_replacements` — pre-type abbreviation normalizations (~200+ entries):
  - `'HWY'`→`'HIGHWAY'`, `'BLVD'`→`'BOULEVARD'`, `'RD'`→`'ROAD'`
  - BIA routes, county roads, state routes, farm roads, etc.

---

## 1.3 ZIP Code Reference Data

### ZIP Code Database Ingestion
- `extract_zip_code_data(zip_code_file_location, output_path, state_codes)`:
  - Stream CSV via `csv.DictReader` with `tqdm` progress tracking
  - Filter rows to valid `state_codes`
  - Standardize ZIP to 5-digit with `clean_standardize_zip()`
  - Clean state with `clean_state()`
  - Clean primary city + all `acceptable_cities` with `clean_standardize_city()`
  - Deduplicate cities via set, sort alphabetically
  - Output Python dict file: `{ "12345": { "cities": [...], "state": "CA", "county": "..." } }`

- `create_zip_code_data(zip_code_file_location, output_path, state_codes, regenerate)`:
  - Conditional wrapper: if output exists and `regenerate=False`, validate with `ast.literal_eval()` before skipping
  - Falls through to extraction on parse failure or `regenerate=True`

### ZIP Reference Structure
- `zip_code_data` dict: keys = 5-digit ZIP strings, values = `{ "cities": [list], "state": "XX", "county": "name" }`

---

## 1.4 String Normalization Functions

- `clean_string(input_string) → str`:
  - Remove non-printable characters via `str.translate()`
  - Collapse multiple spaces to single space
  - Convert to UPPERCASE
  - Strip leading/trailing whitespace

- `clean_standardize_zip(input) → str`:
  - Accept string, int, or float
  - Pad short codes with `zfill(5)` leading zeros
  - Truncate codes > 5 digits
  - Handle ZIP+4: extract first 5 digits
  - Filter non-digit characters with regex

- `clean_state(state, state_codes) → str`:
  - Normalize (strip, uppercase)
  - Check `state_codes` list
  - Look up in `full_state_name_to_two_digit_state_code`
  - Look up in `full_state_name_variations`
  - Return `None` if no match

---

## 1.5 City Name Standardization Pipeline

The full pipeline is orchestrated by `clean_standardize_city()`, which applies all 5 steps in order:

- `clean_standardize_city(input_city_name, input_state_code) → str` — orchestrator:
  1. Remove non-alphanumeric chars (except hyphen/spaces), uppercase, strip
  2. Fix "MC" prefix: regex `"MC ([A-Z])"` → `"MC$1"` (e.g., "MC DONALD" → "MCDONALD")
  3. Remove trailing " UT" artifact
  4. Apply `city_name_word_suffix_correction()`
  5. Apply `city_name_standardize_whole_words()`
  6. Apply `city_name_fix_compound_words()`
  7. Apply `city_name_fix_multiword_strings()`
  8. Apply `state_specific_city_fixes()`
  - Raises `ValueError` if state code invalid

- `city_name_word_suffix_correction(city_name, suffix_substring_dict) → str`:
  - Split city into words; check each word's ending against `suffix_substring_dict` keys
  - Replace matched suffix; stop after first match per word (lazy)

- `city_name_standardize_whole_words(city_name, complete_word_replacement) → str`:
  - Tokenize; strip trailing punctuation per token; look up in `complete_word_replacement_dict`
  - Preserve trailing punctuation in output

- `city_name_fix_compound_words(city_name, compound_corrections_dict) → str`:
  - Convert dict keys to tuples for O(1) lookup on word pairs
  - Consume 2 words when pair matches, 1 word otherwise

- `city_name_fix_multiword_strings(city_name, multi_word_replacement_dict) → str`:
  - Precompile regex patterns with word boundaries (`(?<!\w)` ... `(?!\w)`)
  - Case-insensitive substitution on full uppercase-normalized string

- `state_specific_city_fixes(city_name, state_code, state_specific_replacements) → str`:
  - Fetch state-specific dict from `state_specific_replacements[state_code]`
  - Apply regex word-boundary substitutions for each entry

---

## 1.6 Address Component Normalization

### Directional Standardization
- Detect directionals in wrong fields; move to `st_predir` or `st_posdir`
- `move_directionals(st_name, ...) → (st_name, st_predir, st_posdir)`:
  - Extract leading directionals from `st_name` → `st_predir`
  - Extract trailing directionals from `st_name` → `st_posdir`

### Street Type Detection & Extraction
- `move_street_type(st_name, usps_st_posttyp) → (st_name, st_postyp)`:
  - Check last token(s) of `st_name` against `usps_st_posttyp` list
  - Extract to `st_postyp` if match found

### Unit Pattern Extraction
- `move_unit_numbers(st_name) → (st_name, secondary_address)`:
  - Regex: `[A-Za-z]*\s?\d+\s?[-~/\\]\s?[A-Za-z]*\s?\d+` (e.g., "A 1-B 2")
  - Move matched unit patterns from `st_name` to `secondary_address`

### Secondary Address Assembly
- Concatenate NAD fields: Building + Floor + Unit + Room + Seat with field labels
- Format: e.g., `"UNIT 5 FLOOR 2"`
- Handle unit designator tokens: APT, UNIT, SUITE, STE, BLDG, FL, FLOOR

---

## 1.7 Column-Specific Cleaning Functions (NAD ETL)

These 8 functions clean individual NAD columns with domain-specific logic. All operate on Polars LazyFrames for memory efficiency.

- `transform_column(col_name) → pl.Expr` — baseline: strip + UPPERCASE (applied to all columns)

- `clean_addnum_pre_lazy(lazy_frame, ...) → pl.LazyFrame` — 7-step logic:
  1. Fix integer-directional concatenations: "1N" → `add_number="1N"`, `addnum_pre=""`
  2. Move directional words → `st_predir`
  3. Standardize valid terms: TRAIL MARKER→TM, MILE MARKER→MM, KIOSK
  4. Remove `<NULL>` markers
  5. Remove single letters or hyphen-separated numbers (regex)
  6. Remove keywords: HOUSE, ANT
  7. Default: clear remaining invalid values

- `clean_addnum_suf_lazy(lazy_frame) → pl.LazyFrame`:
  - Retain fractions (1/2, 1/3, 1/4, 2/3, 3/4) and decimals (.1–.9)
  - Move all other text to `secondary_address`
  - Replace NULL/UNKNOWN/empty with null

- `clean_st_premod_lazy(lazy_frame, ...) → pl.LazyFrame` — 8-step logic:
  1. STEPETZ (MN special case) → restructure fields, move to `st_name`
  2. NORTHBOUND/SOUTHBOUND/etc. → `st_posmod`
  3. FM (Farm-to-Market) → `st_pretyp`
  4. Remove 13 known-invalid values *(* **[DATA FILE REQUIRED: `pre_processing_nad_elements.py`]** *— copy the exact list from the source)*
  5. Single letters A–D → `secondary_address`
  6. Full state names → 2-letter codes
  7. Apply `st_premod_replacements` dict
  8. Directional terms → `st_predir`

- `clean_st_predir_lazy(lazy_frame) → pl.LazyFrame`:
  - Remove invalid values: PULASKI, ATTU STATI, JONES, UNKNOWN, etc. **[DATA FILE REQUIRED: `pre_processing_nad_elements.py`]** — copy the complete list; "etc." above is not exhaustive

- `clean_st_pretyp_lazy(lazy_frame, st_pretyp_replacements) → pl.LazyFrame`:
  - Remove UNKNOWN/UNK
  - Apply `st_pretyp_replacements` dict

- `clean_st_name_lazy(lazy_frame, ...) → pl.LazyFrame` — 5-step:
  1. `clean_string()` — non-printable removal, uppercase
  2. `city_name_standardize_whole_words()` — word token standardization
  3. `move_street_type()` — extract USPS post types → `st_postyp`
  4. `move_directionals()` — extract directionals → `st_predir`/`st_posdir`
  5. `move_unit_numbers()` — extract unit patterns → `secondary_address`

- `clean_st_posdir_lazy(lazy_frame) → pl.LazyFrame`:
  - Remove invalid values: IA, ATTU STATI

- `clean_st_posmod_lazy(lazy_frame) → pl.LazyFrame` — 9-step:
  1. Remove numeric/hyphenated-numeric values
  2. Remove if matches `post_city` exactly
  3. Remove 24-entry blacklist **[DATA FILE REQUIRED: `pre_processing_nad_elements.py`]** — copy the exact list from the source
  4. EAST CAROGA → `st_name`
  5. UPSTAIRS → `secondary_address`
  6. KY special: MAZIE/ADAMS/LOUISA/CATLETTSBURG → `post_city` when city is NOT STATED
  7. MA special: (TAUNTON) → `post_city` when city is NOT STATED
  8. IL special: ROYAL LAKES → `post_city` when city is NOT STATED
  9. Oil field variants → `st_name`/`st_postyp`

---

## 1.8 NAD ETL Pipeline

- `setup_logging() → logging.Logger` — INFO level, timestamp format

- `calculate_optimal_batch_size(batch_size) → int`:
  - Query `psutil.virtual_memory().available`
  - Assume 425 bytes/row (NADv17 specific)
  - Return `min(user_batch_size, memory_limit)`

- `create_lazy_chunks(file_path, chunk_size=1_000_000) → generator[pl.LazyFrame]`:
  - Lazy load with lowercase column names
  - Force all 21 columns to UTF-8 string via `schema_overrides`
  - Total rows: 80,321,833 (hardcoded for NADv17)
  - Yield LazyFrame slices of `chunk_size` rows

- `process_nad_file(input_file, output_file, batch_size)` — main ETL orchestrator:
  1. Setup logging + calculate optimal batch size
  2. Iterate lazy chunks
  3. Apply `transform_column` to all columns
  4. Build `secondary_address` from [building, floor, unit, room, seat]
  5. Build `full_address` from components
  6. Apply all 8 cleaning functions in sequence
  7. Save each chunk as temp parquet (zstd compression)
  8. Garbage collect after each chunk
  9. Combine chunk parquets into final output
  10. Delete temp files

- `extract_address_data(nad_input_file, nad_output_file, batch_size=5_000_000, regenerate=False)`:
  - Wrapper: validates existing parquet with `pq.ParquetFile()` before regenerating

- `extract_address_elements_from_national_address_database(input_file, output_file, sample_only=False)`:
  - Extract unique values per column (excluding `full_address`)
  - Polars lazy CSV; force UTF-8; apply `clean_string()`; deduplicate via set; sort
  - Output Python dict file: `parsed_address_elements = { "col": [sorted_unique_values] }`

---

## 1.9 NULL & Missing Value Handling

- Replace `NaN` with empty string (`fillna("")`)
- Remove `<NULL>`, `<NULL` placeholder strings
- Remove `UNKNOWN`, `UNK` (field-specific)
- Replace empty strings with null in Polars context
- Handle `.0` float-to-string artifacts (strip `.0` suffix)

---

## 1.10 Memory & Infrastructure (Phase 1 scope)

- `ProcessPoolExecutor` parallel chunk processing (cpu_count - 1 workers)
- `gc.disable()` during batch processing; re-enable after
- Output formats: Parquet (zstd), Python dict files, CSV

---

---

# PHASE 2 — Parsing
### Rule-Based Extraction · Neural Network Training · Inference Pipeline

**Goal:** Given a raw address string, produce a populated 15-field component dict. Phase 2 contains two tracks that can be developed in parallel: a fast rule-based extractor (no ML, deterministic) and a BERT-based sequence labeling model. Both use Phase 1's normalization layer as preprocessing.

**Deliverables:** `AddressPreprocessor`, `parse_address()` inference function, trained `AddressParser` model checkpoint, and the full training pipeline.

---

## 2.1 Rule-Based Component Extraction

### Address Preprocessor (`AddressPreprocessor` class)

- `__init__(state_codes, full_state_name_variations, full_state_name_to_two_digit_state_code, zip_code_data)`:
  - Store `state_codes` as set for O(1) lookup
  - Regex: `zip_pattern = r'\b\d{5}(?:-?\d{2,4})?\b'` (handles ZIP+4)
  - Regex: `house_number_pattern = r'^\d+'`
  - `unknown_city_variants = {'UNKNOWN', 'NOT STATED', 'UNSTATED', 'UNNAMED', 'NOT AVAILABLE', 'N/A', 'NA', 'NONE'}`

- `get_state_code(state) → str`:
  - Normalize → check `state_codes` set → check variations dict → check full name dict

- `extract_components(address) → Dict`:
  - Split on commas
  - Last segment: ZIP (regex) + state (lookup)
  - Second-to-last: city (unknown variants → `'NOT STATED'`)
  - Remainder: `street_address`
  - Call `validate_city_state_zip()` when all three present

- `preprocess_street_address(street_address) → str`:
  - Add spaces around house numbers (regex callback avoids breaking ZIPs)
  - Add spaces around directionals: `r'\b(N|S|E|W|NE|NW|SE|SW|NORTH|SOUTH|EAST|WEST)\b'`
  - Add spaces around unit designators: `r'\b(APT|UNIT|SUITE|STE|BLDG|FL|FLOOR)\b'`
  - Normalize multiple spaces to single space

- `preprocess(address) → Tuple[str, Dict]`:
  - Call `extract_components()` → `preprocess_street_address()` on street portion
  - Construct tokenizer input: `"street_processed , city , state , zip"`
  - Return `(preprocessed_text, components_dict)`

### City/State/ZIP Hierarchy Validation

- `validate_city_state_zip(city, state, zip_code) → Tuple[str, str, str]`:
  - Extract base 5-digit ZIP
  - If ZIP in `zip_code_data`: compare stored state; correct state mismatch
  - Warn (don't auto-correct) if city not in valid cities for ZIP
  - Unknown city variants bypass city check
  - Return corrected `(city, state, zip_code)`

### Address Component Format Validation

- ZIP: valid if matches `r'\b\d{5}(?:-?\d{2,4})?\b'`
- State: valid if in `state_codes` set
- House number: valid if matches `r'^\d+'`
- `parse_address_string(address_str) → Dict`: regex extraction of `AddressNumber`, `StreetName`, `ZipCode`

---

## 2.2 Synthetic Training Data Generation

- `augment_address_data(address_data) → list`:
  - Always include original record
  - 4+ digit `add_number`: add variation with space after first digit ("1234" → "1 234")
  - Compound `st_name` (with spaces): add variation without spaces
  - Return list: original + augmented records

- `generate_add_number_for_synthetic_data() → int`:
  - Weighted random int from empirical NAD distribution:
    - 1–1,000: 1.68%
    - 1,001–10,000: 11.80%
    - 10,001–100,000: 65.04% (most common)
    - 100,001–1,000,000: 21.46%
    - 1,000,001–10,000,000: 0.02%

- `test_distribution_for_add_number_for_synthetic_data(n_samples=100000) → dict`:
  - Validate generated distribution against expected probability ranges

- `extract_addnum_pre_for_synthetic_data(input_file_name, output_folder_path)`:
  - Polars lazy load; select `[addnum_pre, state]` columns only
  - Remove `.0` artifacts; filter `<NULL>` markers
  - Exclude single-letter prefixes in LA and CT (state-specific data quality rule)
  - Group by value, compute frequency (count / total)
  - Output `addnum_pre.py` with probability dict (9 decimal places)

- Synthetic variation types (notebook-level):
  - Missing address components
  - Typos in street names and city names
  - Alternative abbreviations
  - Spacing variations
  - Directional permutations
  - Unit designator variants

---

## 2.3 Neural Network Training Pipeline

### Configuration

- `AddressParserConfig` dataclass:
  - `batch_size=32`, `max_length=128`, `learning_rate=2e-5`, `num_epochs=5`
  - `mixed_precision=True`, `chunk_size=100_000`, `gradient_accumulation_steps=4`
  - `num_workers=4`, `prefetch_factor=2`
  - `model_save_dir=Path('models')`, `model_name='best_address_parser.pt'`

### Training Data Loading

- `load_data_in_chunks(parquet_path, target_sample_size=1_000_000) → pl.DataFrame`:
  - **Stratified sampling by state** in 3 phases:
    1. Minimum per state: `min(1000, target_size / (num_states × 2))`
    2. Proportional fill of remaining quota by state frequency
    3. Random sampling to fill remaining balance
  - Polars streaming, chunk_size=10,000; cast all columns to UTF-8

### Dataset

- `AddressDataset(Dataset)`:
  - **Chunk-based caching**: pre-tokenize in 1,000-record chunks → `.pt` files in `tokenization_cache/`
  - `_check_cache_complete()`: verify all chunk files exist
  - `_create_label_sequence(address, idx) → torch.Tensor`:
    - Initialize label tensor of length `max_length` to PAD label (15)
    - For each component: tokenize value, find token positions, set label IDs
  - `_process_chunk(start_idx, end_idx)`: batch BERT tokenization + label creation
  - `__getitem__(idx)`: load chunk from file → return `{input_ids, attention_mask, labels}`

### Label Map (16 labels)

```
0: addnum_pre    1: add_number    2: addnum_suf
3: st_premod     4: st_predir     5: st_pretyp
6: st_presep     7: st_name       8: st_postyp
9: st_posdir    10: st_posmod    11: post_city
12: state       13: zip_code     14: secondary_address
15: PAD
```

### Model Architecture — `AddressParser(nn.Module)`

- `bert-base-uncased` as sequence encoder
- Dropout (0.1)
- **Number-specific MultiheadAttention**: 8 heads; `number_mask` for tokens with ASCII values 48–57 (digits); apply attention with digit mask; residual add to sequence output
- Linear classifier: `hidden_size → 16 labels`
- `forward(input_ids, attention_mask) → logits [batch, seq_len, 16]`

### Training Loop

- `train_model(model, train_loader, val_loader, device, config)`:
  - AdamW optimizer, CrossEntropyLoss (ignore_index=-100 for PAD)
  - Mixed precision: `autocast('cuda')` + `GradScaler`
  - Gradient accumulation: 4 steps
  - CUDA cache cleared every 100 batches
  - Validation after every epoch; save best model by lowest val loss

### Address-Specific Training Metrics

- `calculate_metrics(outputs, labels, tokenizer) → dict`:
  - `number_accuracy`: accuracy on `add_number` tokens (label 1) when both are numeric
  - `compound_street_accuracy`: accuracy on `st_name` tokens (label 7) with spaces
  - Both handle `##` subword token reassembly

### Supporting Utilities

- `get_gpu_utilization() → float`: pynvml GPU % query
- `clear_memory()`: Python `gc.collect()` + `torch.cuda.empty_cache()`
- `format_time(seconds) → str`: HH:MM:SS format

### Pipeline Orchestration

- `execute_training_pipeline(nad_output_file, project_root, model_save_dir)`:
  - Detect device (CUDA vs CPU)
  - Load BERT tokenizer
  - `load_data_in_chunks()` → 80/20 train/val split
  - Create `AddressDataset` + `DataLoader` instances
  - Initialize `AddressParser`
  - Call `train_model()`

### Hyperparameter Optimization (Optuna — optional track)

- Search space: embed_dim ∈ {128,256,512}, num_layers ∈ [2,6], num_heads ∈ {4,8,12}, dropout ∈ [0.1,0.3], batch_size ∈ {32,64,128}, lr ∈ [1e-5,1e-3]
- Best known: embed_dim=128, num_layers=5, num_heads=4, dropout=0.2257, batch_size=32, lr=0.000399

---

## 2.4 Inference Pipeline

### Model Loading

- `load_trained_model(model_path, device) → nn.Module`:
  - Initialize `AddressParser(num_labels=16)`
  - Add `AddressParserConfig`, `WindowsPath`, `Path` to PyTorch safe globals
  - Handle both full checkpoint dict (`model_state_dict` key) and raw state dict
  - Set eval mode

- `initialize_tokenizer() → BertTokenizer`:
  - `bert-base-uncased` with logging warning suppression

### Single Address Parse

- `parse_address(model, tokenizer, preprocessor, address, device, max_length=128) → dict`:
  1. `preprocessor.preprocess(address)` → preprocessed text + extracted components
  2. BERT tokenize: `add_special_tokens=True`, `padding='max_length'`, `truncation=True`
  3. `torch.no_grad()` + `autocast` forward pass → logits
  4. `argmax` per token → label IDs
  5. Skip [CLS], [SEP], [PAD] tokens
  6. Reassemble `##` subword tokens (WordPiece)
  7. Group consecutive same-label tokens → component strings
  8. `postprocess_predictions()` → final component dict

### Postprocessing

- `postprocess_predictions(predictions, components, ...) → Dict`:
  - Override model state/ZIP/city with preprocessor-extracted values (higher confidence)
  - Address number correction: if `st_predir` is all digits and `add_number + st_predir ≤ 6 digits` → concatenate to `add_number`, clear `st_predir`
  - Validate final city/state/ZIP against `zip_code_data`

### Batch Parse

- `parse_addresses(addresses, model_path) → List[dict]`: loads model + tokenizer; iterates with `tqdm`

### Alternative: usaddress Library (third-party fallback)

- Referenced for probabilistic parsing without a trained model
- Useful as fallback or comparison baseline

---

## 2.5 Environment Detection (Phase 2 scope)

- `EnvironmentManager._detect_basic_environment()`: OS, platform, physical/logical CPU count, total/available memory, Python version
- `EnvironmentManager._detect_gpu_environment()`: `torch.cuda.is_available()`; per-GPU name + memory + version; graceful ImportError
- `EnvironmentManager.get_processing_environment()`: GPU path (`device='cuda'`, `parallel_processes=1`) vs CPU path (`device='cpu'`, `parallel_processes=cores-1`)
- `EnvironmentManager.validate_environment()`: minimum 4 GB RAM + 2 cores

---

---

# PHASE 3 — Validation & Geocoding
### Coordinate Verification · Multi-Source Cascade · Confidence Scoring · Caching

**Goal:** Given a parsed address + lat/lon coordinates, determine whether the coordinates are valid for that address, attempt correction if not, and return a structured result with a calibrated confidence score. All API integrations and caching live here.

**Deliverables:** `AddressValidationService`, all data source adapters, `BuildingFootprintValidator`, `BuildingClassifier`, `ConfidenceCalculator`, SQLite caches, and the full validation result schema.

---

## 3.1 Validation Result Schema

Every validation function returns a structured dict with:

```python
{
  "timestamp": str,               # ISO 8601
  "input_address": dict,          # original address components
  "input_coordinates": dict,      # original lat/lon
  "coordinates_valid": bool,
  "confidence_score": float,      # 0–1, 3 decimal places
  "validation_method": str,       # "polygon_match" | "coordinate_correction" | "direct_match" | "failure"
  "data_source": str,
  "building_type": str,           # from BuildingClassifier
  "building_info": dict,
  "corrected_coordinates": dict,  # if correction applied
  "original_coordinates": dict,
  "coordinate_updated": bool,
  "address_match_score": float,
  "distance": float,              # meters
  "osm_id": str,
  "validation_timestamp": str,
  "metadata": {
    "attempted_sources": list,
    "validation_count": int,
    "consensus_score": float
  }
}
```

---

## 3.2 Data Source Interfaces

### Abstract Base

- `DataSource(ABC)`:
  - `name` property → str
  - `validate_location(request) → Dict`
  - `attempt_correction(request) → Dict`

- `BaseDataSource(ABC)`:
  - `Cache` (SQLite, TTL-aware), `RateLimiter` (token bucket)
  - `_make_request(url, params, timeout=30) → Dict`: HTTP GET with rate limiting + error handling

### OpenStreetMap / Nominatim

- `OpenStreetMapSource.validate_location(request) → Dict`:
  - `GET /reverse?lat=&lon=&format=json&addressdetails=1&extratags=1`
  - Check `osm_type=='way'` with `'building'` extratag
  - Return `coordinates_valid=True`, `confidence_score=0.9` if building found
  - Graceful JSON decode error handling

- `OpenStreetMapSource.attempt_correction(request) → Dict`:
  - Construct query: `"street_number street_name, city, state postal_code"`
  - `GET /search?q=<address_string>`
  - Calculate geodesic distance to first result
  - Accept correction if `distance ≤ 100 meters`

- `OpenStreetMapSource._find_best_match(request, candidates) → Optional[Dict]`:
  - Score: `0.7 × address_score + 0.3 × distance_factor`
  - Require `confidence ≥ 0.8`

- `OpenStreetMapSource._respect_rate_limit()`: token bucket, 1 req/sec (Nominatim policy)
- `OpenStreetMapSource._calculate_distance(lat1, lon1, lat2, lon2) → float`: pyproj geodesic inverse → meters

**API details:** Base URL `https://nominatim.openstreetmap.org`, User-Agent header required, rate limit 1 req/sec

### Microsoft Building Footprints (optional)

- `MicrosoftBuildingFootprintsDataSource.validate_coordinates(lat, lon) → Dict`:
  - Microsoft Maps Atlas API
  - 50m radius building polygon search
  - Requires `MICROSOFT_MAPS_KEY` env var
  - Return `coordinates_valid=True` if polygons found; extract `polygon_count`, `sourceDate`
  - Rate limit: 5 req/sec

### Local Building Footprints Database

- Schema: `building_footprints` table: `id, lat_min, lat_max, lon_min, lon_max, building_type, metadata (JSON)`
- Index on `(lat_min, lat_max, lon_min, lon_max)`
- `validate_coordinates(lat, lon) → Dict`: bounding-box query → `confidence_score=0.95` if match
- `get_nearby_footprints(lat, lon, radius=50) → List[Dict]`: convert radius to lat/lon delta → bounds query → GeoJSON format
- `get_nearby_buildings_with_addresses(lat, lon, max_distance=50) → List[Dict]`: above + address from metadata JSON
- `_init_database()`: create schema + seed with sample data if empty

### Data Source Manager

- `DataSourceManager.__init__(cache_path=None)`: auto-add OSM (always), Microsoft (if key present), local (if available)
- `DataSourceManager.add_source(source)`: register additional source
- `DataSourceManager.validate_coordinates(lat, lon) → Dict`: try all sources sequentially; collect results + errors
- `DataSourceManager._aggregate_results(results) → Dict`:
  - Sort by `confidence_score` DESC
  - Return best result with `alternative_sources`, `validation_count`, `consensus_score`

---

## 3.3 Address Matching

- `AddressMatcher.compare_addresses(addr1, addr2) → Dict`:
  - House number: exact match, **40% weight**
  - Street name: Levenshtein similarity (0–1), **30% weight**
  - Postal code: exact match, **20% weight**
  - City/state: case-insensitive exact, **10% weight**
  - Return `{component_scores, overall_score}`

- `AddressMatcher._calculate_string_similarity(str1, str2) → float`: Levenshtein distance, fallback exact

- `AddressMatcher._normalize_street(street) → str`:
  - `street→st, avenue→ave, boulevard→blvd, drive→dr, road→rd, lane→ln, circle→cir, court→ct`

- `AddressValidator.calculate_similarity(addr1, addr2) → float`:
  - Parse both addresses; character-by-character comparison per component; return average

---

## 3.4 Coordinate Validation & Correction

### Point-in-Polygon

- `GeometryValidator.point_in_polygon(lat, lon, polygon_coords) → bool`:
  - `Point(lon, lat).within(Polygon(coords))` — Shapely
  - Attempt `buffer(0)` fix on invalid geometry before raising `GeometryError`

### Distance Calculation

- `GeometryValidator.calculate_distance_to_polygon(lat, lon, polygon_coords) → float`:
  - Return 0.0 if point within polygon
  - `shapely.ops.nearest_points()` → closest boundary point
  - `pyproj.Geod.inv()` (WGS84) → distance in meters

### Building Area & Centroid

- `_calculate_building_area(coordinates) → float`: `Polygon.area × 111000²` (lat/lon → meters approximation)
- `_calculate_centroid(coordinates) → Tuple[float, float]`: `Polygon.centroid` → `(lat, lon)`

### Full Coordinate Validation

- `BuildingFootprintValidator.validate_coordinates(lat, lon, address=None) → Dict`:
  1. `_validate_with_local_footprints(lat, lon)` → polygon match check
  2. `_validate_with_address(lat, lon, address)` → address similarity check
  3. `_validate_with_osm(lat, lon)` → OSM reverse geocode fallback
  - Return `coordinates_valid, confidence_score, validation_method, building_type, distance_to_building, address_match`

### Coordinate Correction

- `BuildingFootprintValidator._attempt_coordinate_correction(lat, lon, address) → Dict`:
  - Find buildings with `address_match_score ≥ 0.8`
  - Select largest building by polygon area if multiple
  - Compute centroid as corrected coordinates
  - Confidence: `(0.7 × address_score) + (0.3 × distance_factor)` where `distance_factor = max(0, 1 - distance_meters/50)`
  - Apply only when `confidence_score ≥ 0.8`

- `_find_matching_building(lat, lon, address) → Dict`:
  - Score candidates: `0.7 × address_similarity + 0.3 × distance_factor`
  - Require `address_similarity ≥ 0.8`

---

## 3.5 Confidence Scoring

### Address Match Score
```
address_match = (0.4 × house_number_exact) + (0.3 × street_name_similarity)
              + (0.2 × postal_code_exact) + (0.1 × city_state_exact)
```

### Composite Validation Confidence
```
confidence = (0.5 × address_match) + (0.3 × building_match) + (0.2 × source_reliability)
```

### Source Reliability Scores
| Source | Score |
|---|---|
| local_database | 1.0 |
| google_maps | 0.9 |
| microsoft | 0.85 |
| openstreetmap | 0.8 |
| unknown | 0.7 |

### Distance-Based Confidence
| Distance | With address match | Without |
|---|---|---|
| 0m (inside polygon) | 1.0 | 0.9 |
| ≤ 5m | 0.8 | 0.7 |
| ≤ 10m | 0.6 | 0.5 |
| ≤ 20m | 0.4 | 0.3 |
| > 20m | 0.0 | 0.0 |

Bonus: address match +0.2; building type match +0.1; capped at 1.0

### Coordinate Correction Confidence
```
distance_factor = max(0, 1 - distance_meters / 50)
confidence = (0.7 × address_similarity) + (0.3 × distance_factor)
```

### Consensus Score
```
consensus_score = sources_confirming_valid / total_sources_tested
```

- `ConfidenceCalculator.calculate_confidence(address_match, building_match, source_reliability) → float`: weighted formula, rounded to 3 decimals
- `ConfidenceCalculator.calculate_source_reliability(source_name) → float`: lookup table

---

## 3.6 Building Classification

- `BuildingType(Enum)`: `RESIDENTIAL_SINGLE, RESIDENTIAL_MULTI, COMMERCIAL, INDUSTRIAL, INSTITUTIONAL, MIXED_USE, UNKNOWN`

- `BuildingClassifier.classify_building(footprint_data, osm_data=None, address_data=None, parcel_data=None) → Dict`:
  - Run up to 4 classifiers; combined confidence = `sum(scores) / num_sources`

- `_classify_by_footprint(footprint_data) → Dict`:
  - ≤ 5,000 sq ft → RESIDENTIAL_SINGLE (0.7)
  - ≥ 2,000 sq ft → COMMERCIAL (0.6)
  - Otherwise → UNKNOWN (0.3)

- `_classify_by_osm(osm_data) → Dict`:
  - `house/residential` → RESIDENTIAL_SINGLE (0.8)
  - `apartments` → RESIDENTIAL_MULTI (0.8)
  - `office/retail/commercial` → COMMERCIAL (0.8)
  - `industrial` → INDUSTRIAL (0.8)

- `_classify_by_address(address_data) → Dict`:
  - Residential regex patterns (street types, house, apartment) → RESIDENTIAL_SINGLE (0.6)
  - Commercial regex patterns (suite, office, LLC) → COMMERCIAL (0.6)

- `_classify_by_parcel(parcel_data) → Dict`:
  - Zoning codes: R1→RESIDENTIAL_SINGLE, R2→RESIDENTIAL_MULTI, C1→COMMERCIAL, I1→INDUSTRIAL, Mixed→MIXED_USE (all 0.9)

---

## 3.7 Validation Service Layer

### Core Service

- `AddressValidationService.__init__(config_path=None)`: creates `AddressMatcher`, `BuildingFootprintValidator`, `ConfidenceCalculator`
- `AddressValidationService.validate_and_correct(address, coordinates) → Dict`:
  - Cascade through sources: local DB → OSM → fallback
  - Direct match → return success; invalid coords → attempt correction; all fail → failure
  - Return full structured validation result

### Cached Service

- `AddressValidationService.validate_address(input_data, skip_cache=False) → Dict`:
  - Check cache first; validate with OSM; cache if valid
  - Required input keys: `street_number, street_name, city, state, postal_code, latitude, longitude`

### Module-Level Functions

- `process_address(address, output_file) → Dict`:
  - Validate; update coordinates if `confidence_score ≥ 0.8` and correction applied
  - Append JSON result to output file

- `process_address_batch(addresses, output_file) → List[Dict]`: batch wrapper

- `validate_single_address(lat, lon, cache_dir) → Dict`
- `validate_address_batch(addresses, cache_dir) → List[Dict]`
- `validate_addresses_from_dataframe(df, lat_col, lon_col, cache_dir) → DataFrame`: validate pandas DataFrame; append validation result columns

---

## 3.8 Caching & Persistence

### Validation Cache (SQLite)

- `ValidationDatabaseManager.__init__(database_path)`:
  - Create `cache/` directory if needed
  - Initialize schema; threading lock

- Schema — `validated_addresses` table:
  - `id, street_number, street_name, city, state, postal_code`
  - `original_latitude, original_longitude, validated_latitude, validated_longitude`
  - `validation_date, validation_source, confidence_score, required_correction, building_type`
  - UNIQUE constraint on address components
  - Indexes on `(street_number, street_name, city, state, postal_code)`, coordinates, validation_date

- Schema — `validation_history` table:
  - `id, validated_address_id (FK), validation_date, validation_source, validation_result (JSON), error_message, processing_time`

- `cache_validation_result(address, original_coords, validation_result, processing_time)`: INSERT OR REPLACE; add history entry; thread-safe via `threading.Lock()`
- `get_cached_validation(address) → Optional[Dict]`: exact address lookup
- `get_validation_history(address) → List[Dict]`: all attempts DESC by date
- `cleanup_old_records(days_to_keep=90) → int`: delete old history + orphaned addresses
- `get_statistics() → Dict`: `{total_addresses, corrected_addresses, average_confidence, validation_sources: {name: count}}`

### Geocoding Cache (SQLite, TTL)

- `Cache.__init__(cache_path, ttl_days=30)`: create `cache_entries` table + `idx_timestamp`
- `Cache.generate_key(params) → str`: SHA256 hash of sorted JSON params
- `Cache.get(params) → Optional[Dict]`: return if not expired
- `Cache.set(params, value, source, metadata)`: store with TTL
- `Cache.cleanup() → int`: remove expired entries

### Rate Limiting

- `RateLimiter(requests_per_second)`: token bucket implementation
- `acquire() → bool`: refill tokens by elapsed time; return False if rate-limited
- Nominatim: 1 req/sec (hard Nominatim policy)
- Microsoft Maps: 5 req/sec (configurable)
- Local DB: no limit

---

## 3.9 Error Handling

- Custom exception hierarchy:
  - `DataSourceError` (base)
  - `RateLimitError(DataSourceError)`
  - `ValidationError(DataSourceError)`
  - `GeometryError`
  - `ValidationSourceError`
- Per-source try/except with error logging; failed sources tracked in `attempted_sources`
- `_create_failure_result()` / `_create_correction_failure()`: standardized failure response dicts
- JSON decode error handling in Nominatim responses
- Geometry fix: `buffer(0)` on invalid polygons before raising `GeometryError`

---

## 3.10 USPS & Google APIs (Planned Integrations)

- USPS Address Validation API: validate deliverability; standardize to USPS format
- Google Maps Geocoding API: geocode addresses; validate coordinates
- `geopy` library: geocoding abstraction layer

---

---

# PHASE 4 — Enrichment, Scale & Analytics
### Geographic Enrichment · Census Data · Batch Operations · Production Infrastructure

**Goal:** Layer geographic and demographic context onto validated addresses. Add production-grade batch processing, parallel execution, adaptive infrastructure, and all output formats. Phase 4 transforms the library into a full data pipeline capable of processing millions of records.

**Deliverables:** ZIP grain table generator, Census + HUD integration, H3 spatial binning, property dataset schema, parallel batch processor, and all export adapters.

---

## 4.1 ZIP Code Grain Table (22 fields)

- `ZipCodeDataGenerator` class

- `_load_reference_data()`:
  - 50 states: name, FIPS code, Census region, Census division
  - ISO state codes (AL=01, CA=04, etc.)

- `_clean_text(text) → str`:
  - Lowercase; remove unprintable chars; Unicode NFKD normalization + remove combining characters; collapse whitespace

- `_fetch_census_data()`:
  - 2020 ACS 5-Year Estimates via `https://api.census.gov/data/2020/acs/acs5`
  - Variables: NAME, B01003_001E (population), B19013_001E (median income), B25077_001E (median home value), B25003_002E (owner-occupied), B25003_003E (renter-occupied)
  - Geography: `zip code tabulation area:*` (all ZCTAs)
  - `pd.to_numeric()` for numeric conversion

- `_fetch_hud_crosswalk()`: HUD-USPS ZIP-to-county/CBSA crosswalk

- `generate_zip_data(output_file)`:
  1. Fetch Census + HUD data
  2. Merge on ZIP code
  3. Map state FIPS → abbreviations → names/regions/divisions
  4. Calculate derived fields
  5. Determine ZIP type
  6. Add geographic indicators
  7. Clean and validate
  8. Write 22-column CSV

### Derived Fields

- `total_housing_units = owner_occupied + renter_occupied`
- `owner_occupied_pct = (owner / total) × 100`
- `population_density = population / land_area_sqmi`

### ZIP Type Classification

- `_determine_zip_type(df)`:
  - PO Box: `population == 0`
  - Military: ZIP starts with `096`
  - Standard: has housing units

### Urbanization Classification

- `_add_geographic_indicators(df)`:
  - `urban_core`: ≥ 3,000 people/sq mi
  - `urban_fringe`: ≥ 1,000 people/sq mi
  - `suburban`: ≥ 500 people/sq mi
  - `rural`: < 500 people/sq mi

### Output Schema (22 columns)

`zip_code, zip_type, state_abbrev, state_name, iso_state_code, county, county_fips, region, division, cbsa, cbsa_type, urbanization_level, latitude, longitude, population, population_density, median_household_income, median_home_value, total_housing_units, owner_occupied_units, renter_occupied_units, owner_occupied_pct`

### Data Quality

- `_clean_and_validate(df)`: strip whitespace from string columns; zero-fill ZIP to 5 digits; replace inf/NaN in density; type casting
- `_write_output(df, output_file)`: reorder columns; write CSV; log data quality metrics (total ZIPs, missing values, dtypes)

---

## 4.2 Region & Division Classification

- All 50 states + DC mapped to 4 Census regions (Northeast, Midwest, South, West)
- All states mapped to 9 Census divisions
- ISO state code numeric mapping (AL=01, CA=04, etc.)
- FIPS code mappings
- `bound_directionals_dict`: NB→NORTHBOUND, etc.

---

## 4.3 Census ZCTA Spatial Integration

- `data_prep_pipeline`:
  - Download US Census income data at ZCTA level
  - `geopandas` spatial join: property coordinates → ZCTA boundaries
  - Income bracket classification from Table S1901 (Income in the Past 12 Months)
  - Export Delta table for downstream visualization

---

## 4.4 H3 Hexagonal Spatial Binning

- Generate H3 hexagonal indexes for property lat/lon coordinates
- Spatial join of property records to H3 cells
- Aggregate metrics per H3 cell (property count, avg risk attributes, avg income, etc.)
- Used for map aggregation in visualization and aggregation modeling

---

## 4.5 Property Dataset Schema (36 fields)

Full schema for geocoded property-level insurance dataset:

| Category | Fields |
|---|---|
| Identifiers | `policy_key, location_key` |
| Address | `address, city, county, state, zip_code` |
| Coordinates | `latitude, longitude` |
| Geography | `region, division` |
| Property | `roof_type, roof_shape, roof_age, roof_life, electrical_system_type, electrical_system_capacity, plumbing_material, water_heater_age, home_size, home_age, home_value, household_income` |
| Insurance | `fire_protection_class` (ISO 1–10), `distance_to_fire_station_miles, coverage_a_amount` |

---

## 4.6 Geographic Risk Enrichment (Roadmap Items)

Planned capabilities from project roadmap:

- Distance to coast calculation
- Elevation data enrichment
- Fire risk zone classification
- Hurricane exposure band
- Wildfire risk proximity
- Aggregation modeling support (property clustering by geography)
- Catastrophe model integration points (fire, hurricane, wildfire)
- Growth opportunity analysis by geographic segment

---

## 4.7 Parallel Chunk Processing

- `ProcessPoolExecutor` with `cpu_count - 1` workers
- `process_chunk(chunk_id)`: worker function — process single chunk, save temp parquet
- `process_file_parallel()`: orchestrate parallel workers → lazy combine → merge → compress → cleanup
- `gc.disable()` during processing; re-enable after
- Handles 80.3M rows; ~30 min total with parallelization

---

## 4.8 Environment Detection & Adaptive Configuration

- `EnvironmentManager.get_optimal_batch_size() → int`:
  - `usable_memory = available_memory × 0.2`
  - `optimal = usable_memory / 500 bytes`
  - Clamped to [100, 10,000]

- `EnvironmentManager.get_processing_environment() → Tuple[str, Dict]`:
  - GPU: `device='cuda'`, `parallel_processes=1`, `batch_size`, `memory_limit`
  - CPU: `device='cpu'`, `parallel_processes=cores-1`, `batch_size`, `memory_limit`

- `EnvironmentManager.get_environment_summary() → Dict`:
  - `environment_type, configuration, system_info, optimal_batch_size, validation_status`

---

## 4.9 DataFrame Batch Operations

- `validate_addresses_from_dataframe(df, lat_col='latitude', lon_col='longitude', cache_dir='cache') → DataFrame`:
  - Validate all rows; append validation result columns to output DataFrame
  - Returns enriched DataFrame with `coordinates_valid, confidence_score, building_type, validation_method, corrected_latitude, corrected_longitude`

- `validate_address_batch(addresses, cache_dir) → List[Dict]`: batch list validation
- `process_address_batch(addresses, output_file) → List[Dict]`: batch with file output

---

## 4.10 Output Formats

| Format | Used For |
|---|---|
| Parquet (zstd) | NAD output, training data, intermediate ETL |
| SQLite | Validation cache, footprint DB, geocoding cache |
| Python dict files | ZIP reference, address element dictionaries |
| CSV | Property datasets, raw addresses, ZIP grain table |
| JSON (appended) | Individual validation results |
| PyTorch `.pt` | Model checkpoints, tokenization cache chunks |
| Delta table | Streamlit/BI visualization |

---

## 4.11 External Dependencies

| Library | Phase | Purpose |
|---|---|---|
| `polars` | 1, 2, 4 | Lazy/streaming large CSV processing, ETL |
| `pandas` | 1, 4 | DataFrame manipulation, Census data |
| `torch` / `transformers` | 2 | Neural network training and inference |
| `requests` | 3 | HTTP requests to Nominatim, Microsoft, Census APIs |
| `Levenshtein` | 3 | Street name string similarity |
| `pyproj` | 3 | Geodesic distance calculations (WGS84) |
| `shapely` | 3 | Point-in-polygon, nearest_points, centroid |
| `geopandas` | 4 | Spatial joins (properties → ZCTA boundaries) |
| `h3` | 4 | Hexagonal spatial binning |
| `sqlite3` | 3 | Validation cache, footprint DB, geocoding cache |
| `psutil` | 1, 4 | System memory and CPU detection |
| `optuna` | 2 | Hyperparameter optimization |
| `tqdm` | 1, 2 | Progress bars |
| `pynvml` | 2 | GPU utilization monitoring |
| `tokenizers` | 2 | Custom whitespace WordLevel tokenizer |
| `pyarrow` | 1, 2, 4 | Parquet file handling |
| `csv` / `ast` | 1 | ZIP code database processing |

---

## 4.12 External Data Sources

| Source | Phase | Data |
|---|---|---|
| US DOT NAD v17 | 1, 2 | 80.3M US addresses, 31 GB |
| US ZIP Code Database | 1 | ZIP → cities/state/county |
| OpenStreetMap / Nominatim | 3 | Building tags, reverse/forward geocoding |
| Microsoft Building Footprints | 3 | Building polygons (optional) |
| US Census Bureau ACS 5-Year (2020) | 4 | Population, income, housing by ZCTA |
| HUD-USPS Crosswalk | 4 | ZIP → county/CBSA |
| USPS Pub 28 | 1 | Addressing standards (reference) |
| USPS Address Validation API | 3 | Deliverability (planned) |
| Google Maps Geocoding API | 3 | Geocoding (planned) |

---

*End of Phased Brief*
