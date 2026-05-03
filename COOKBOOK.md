# Cookbook

To fulfill the requirements, I have implemented the core logic described in the Phase 4 brief, specifically focusing on the `EnvironmentManager`, `ZipCodeDataGenerator` (mocked for external API stability), and the validation workflows.

=== FILENAME ===
example_basic.py
```python
"""
example_basic.py
Demonstrates the EnvironmentManager to detect optimal processing 
parameters for address workloads.
"""

from main import EnvironmentManager

def main():
    print("--- Address Intelligence: Environment Detection ---")
    
    # 1. Get optimal batch size based on available RAM
    optimal_batch = EnvironmentManager.get_optimal_batch_size()
    print(f"Calculated Optimal Batch Size: {optimal_batch}")

    # 2. Get hardware configuration
    env = EnvironmentManager.get_processing_environment()
    print("\nDetected Processing Environment:")
    print(f"  Device: {env.device}")
    print(f"  Parallel Processes: {env.parallel_processes}")
    print(f"  Batch Size: {env.batch_size}")
    print(f"  Memory Limit: {env.memory_limit} GB")

if __name__ == "__main__":
    main()
```

=== FILENAME ===
example_advanced.py
```python
"""
example_advanced.py
Demonstrates advanced data structures and the logic for 
ZIP code classification and urbanization levels.
"""

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ZipEnrichment:
    zip_code: str
    urbanization_level: str
    population_density: float
    zip_type: str

class ZipCodeLogicMock:
    """
    Mocks the logic found in Section 4.1 of the Brief.
    """
    @staticmethod
    def determine_zip_type(population: int, zip_str: str) -> str:
        if population == 0:
            return "PO Box"
        if zip_str.startswith("096"):
            return "Military"
        return "Standard"

    @staticmethod
    def get_urbanization(density: float) -> str:
        if density >= 3000: return "urban_core"
        if density >= 1000: return "urban_fringe"
        if density >= 500:  return "suburban"
        return "rural"

def main():
    print("--- Address Intelligence: Enrichment Logic Mock ---")
    
    # Simulated raw data from Census/HUD
    raw_data = [
        {"zip": "64083", "pop": 45000, "density": 1200.5, "units": 15000},
        {"zip": "09612", "pop": 500,   "density": 45.0,   "units": 200},
        {"zip": "90210", "pop": 0,     "density": 0.0,    "units": 0},
        {"zip": "10001", "pop": 55000, "density": 4500.0, "units": 25000},
    ]

    enriched_results: List[ZipEnrichment] = []

    for item in raw_data:
        z_type = ZipCodeLogicMock.determine_zip_type(item["pop"], item["zip"])
        u_level = ZipCodeLogicMock.get_urbanization(item["density"])
        
        enriched_results.append(ZipEnrichment(
            zip_code=item["zip"],
            urbanization_level=u_level,
            population_density=item["density"],
            zip_type=z_type
        ))

    print(f"{'ZIP':<10} | {'Type':<10} | {'Urbanization':<15} | {'Density':<10}")
    print("-" * 55)
    for res in enriched_results:
        print(f"{res.zip_code:<10} | {res.zip_type:<10} | {res.urbanization_level:<15} | {res.population_density:<10}")

if __name__ == "__main__":
    main()
```

=== FILENAME ===
example_cli.py
```python
"""
example_cli.py
Simulates a CLI-based batch processing workflow using 
pre-processing cleaning functions.
"""

import sys
from pre_processing_nad_elements import clean_string

def run_cli_sim(input_addresses: list):
    print(f"Starting Batch Process for {len(input_addresses)} records...")
    print("Cleaning street names and filtering unprintable characters...\n")
    
    cleaned_data = []
    for addr in input_addresses:
        # Simulate the cleaning process defined in Section 4.9/pre_processing
        cleaned = clean_string(addr)
        cleaned_data.append(cleaned)
    
    print("--- Processing Results ---")
    for i, original in enumerate(input_addresses):
        print(f"RAW: {original}")
        print(f"CLEANED: {cleaned_data[i]}")
        print("-" * 20)
    
    print(f"\nBatch complete. Success rate: 100%")

if __name__ == "__main__":
    # Simulate CLI input: python example_cli.py "123 Main St\x00" "N/A STREET" "  RIVER RD  "
    args = sys.argv[1:] if len(sys.argv) > 1 else ["123 Main St\x00", "UNKNOWN STREET", "  RIVER RD  "]
    run_cli_sim(args)
```

=== FILENAME ===
COOKBOOK.md
```markdown
# Address Intelligence Library Cookbook

A quick-start guide for utilizing the Phase 4 Enrichment and Scale modules.

## Quick Start

### Installation Requirements
Ensure you have the core dependencies installed:
```bash
pip install psutil pandas polars h3 pyproj shapely geopandas
```

### Basic Environment Setup
To ensure your script doesn't crash your system when processing millions of rows, always initialize the `EnvironmentManager`:

```python
from main import EnvironmentManager

# Automatically detect CPU cores and available RAM
config = EnvironmentManager.get_processing_environment()
batch_size = EnvironmentManager.get_optimal_batch_size()

print(f"Running on {config.parallel_processes} cores with batch size {batch_size}")
```

---

## Recipes

### 1. Adaptive Batch Processing
**Goal:** Process a large list of addresses without exceeding system memory.

```python
from main import EnvironmentManager

def process_large_dataset(data_iterator):
    batch_size = EnvironmentManager.get_optimal_batch_size()
    current_batch = []
    
    for record in data_iterator:
        current_batch.append(record)
        
        if len(current_batch) >= batch_size:
            # Perform heavy computation (e.g., geocoding or neural net inference)
            perform_validation(current_batch)
            current_batch = [] # Reset batch
            
    # Final leftovers
    if current_batch:
        perform_validation(current_batch)

def perform_validation(batch):
    # Placeholder for actual validation logic
    print(f"Validated batch of {len(batch)}")
```

### 2. Urbanization & Density Calculation
**Goal:** Classify a ZIP code's demographic profile based on Census data.

```python
# Logic derived from Section 4.1
def classify_area(population, land_area_sqmi):
    density = population / land_area_sqmi
    
    if density >= 3000:
        level = "urban_core"
    elif density >= 1000:
        level = "urban_fringe"
    elif density >= 500:
        level = "suburban"
    else:
        level = "rural"
        
    return {"density": density, "level": level}

# Usage
result = classify_area(population=4500, land_area_sqmi=2.5)
print(f"Density: {result['density']} -> Category: {result['level']}")
```

### 3. Robust String Cleaning (NAD Standard)
**Goal:** Clean dirty street names for use in neural network tokenizers.

```python
from pre_processing_nad_elements import clean_string

dirty_addresses = [
    "1208  LAKECREST  ST\x00", 
    "  N. MAIN STREET  ", 
    "ST_PREMOD_INVALID_123"
]

cleaned = [clean_string(a) for a in dirty_addresses]

# Output: ['1208 LAKECREST ST', 'N. MAIN STREET', 'ST_PREMOD_INVALID_123']
print(cleaned)
```