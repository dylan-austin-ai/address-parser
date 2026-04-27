# This file contains the manipulations required to preprocess the National Address Database, including:
#	- Cleaning strings by trimming and forcing to uppercase
# 	- Correcting locations of errored elements

# EXAMPLE CALL
# input_file = r'C:\Users\dylan\Desktop\Professional\Articles\address_parsing_neural_net\data\national_address_database\TXT\NAD_r17.txt'
# output_file = r'C:\Users\dylan\Desktop\Professional\Articles\address_parsing_neural_net\data\national_address_database\nad_output.parquet'
# process_file(input_file, output_file, batch_size=5000000) 


# Needed libraries
import psutil
import os
import polars as pl
import gc
import logging
import re
import multiprocessing
import pyarrow.parquet as pq

# Import local files
import sys
from pathlib import Path
project_root = Path.cwd().parents[0]  # Get the absolute path to the project root. Moves up from "notebooks" to "address_parsing_neural_net"
sys.path.append(str(project_root / "src")) # Add 'src' to sys.path

# Import the modules
from address.address_functions import *
from address.address_reference import *
from address.united_states_zipcodes_functions import *
from address.national_address_database_functions import *

# Helper Functions

# Setup logging
def setup_logging() -> logging.Logger:
    """
    Configure and initialize the logging system for the application.
    
    Sets up basic logging configuration with INFO level and a timestamp format.
    The format includes timestamp, log level, and message components.
    
    Returns:
        logging.Logger: Configured logger instance ready for application-wide logging.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)

# Function to calculate available memory and optimal batch size
def calculate_optimal_batch_size(batch_size: int) -> int:
    """
    Calculate the optimal batch size based on available system memory and input parameters.
    
    This function determines the maximum number of rows that can be safely processed
    in memory given the current system resources. It considers:
    - Available system RAM
    - Average row size (425 bytes for NADv17 dataset)
    - User-specified batch size
    
    Args:
        batch_size (int): The desired batch size specified by the user
        
    Returns:
        int: The smaller of either the input batch size or the maximum safe batch size
            based on available memory
            
    Note:
        The function assumes an average row size of 425 bytes, which is specific to
        the NADv17 dataset structure. This may need adjustment for different datasets.
    """
    if not isinstance(batch_size, int):
        raise TypeError("Batch size must be an integer")
    if batch_size <= 0:
        raise ValueError("Batch size must be positive")
    
    available_memory = psutil.virtual_memory().available
    available_memory_gb = available_memory / (1024**3)
    
    avg_row_size = 425
    rows_in_memory = available_memory // avg_row_size
    
    optimal_size = min(rows_in_memory, batch_size)
    
    logging.info(f"Available memory: {available_memory_gb:.2f} GB")    
    logging.info(f"An estimated {rows_in_memory} rows can fit into memory")
    logging.info(f"Optimal batch size based on input batch size: {optimal_size}")
    
    return optimal_size

# Processing
# Function to define standard cleaning of a polars lazyframe column
def transform_column(col_name: str) -> pl.Expr:
    """
    Apply standard string cleaning transformations to a Polars LazyFrame column.
    
    Applies the following transformations in sequence:
    1. Strips leading and trailing whitespace
    2. Converts text to uppercase
    
    Args:
        col_name (str): Name of the column to transform
        
    Returns:
        pl.Expr: A Polars expression representing the transformed column
    """
    return pl.col(col_name).str.strip_chars().str.to_uppercase().alias(col_name)

# Function to create lazy_chunks
def create_lazy_chunks(file_path: str, chunk_size: int = 1_000_000) -> pl.LazyFrame:
    """
    Create an iterator of lazy-loaded chunks from a large CSV file.
    
    This function handles the efficient loading of large CSV files by:
    1. Converting column names to lowercase
    2. Forcing specific data types for columns
    3. Selecting only needed columns
    4. Creating chunks of specified size
    
    Args:
        file_path (str): Path to the input CSV file
        chunk_size (int, optional): Number of rows per chunk. Defaults to 1,000,000
        
    Yields:
        pl.LazyFrame: Lazy-loaded chunk of data with standardized column names and types
        
    Note:
        The total rows count is currently hardcoded to 80,321,833 for optimization.
        To recalculate, uncomment the pl.scan_csv() line.
    """
    
    # Define columns to retain in the output
    columns_to_keep = [
        "addnum_pre", "add_number", "addnum_suf", "st_premod", "st_predir", 
        "st_pretyp", "st_presep", "st_name", "st_postyp", "st_posdir", 
        "st_posmod", "post_city", "state", "zip_code", "longitude", "latitude",
        "addrclass", 'building', 'floor', 'unit', 'room', 'seat', 'addno_full',
        'stnam_full'
    ]
    
    # Force all columns to UTF-8 string type for consistency
    force_to_string = {col: pl.Utf8 for col in columns_to_keep}

    # Hardcoded total rows - uncomment scan_csv line to recalculate
    total_rows = 80321833 ## UNCOMMENT THIS!  Commented so it doesn't have to recalculate each time. pl.scan_csv(file_path).select(pl.len()).collect().item()
    
    # Get total rows first - note this will scan the file once
    total_rows = 80321833 

    # Yield lazy-loaded chunks of the specified size
    for offset in range(0, total_rows, chunk_size):
        yield pl.scan_csv(
            file_path,
            with_column_names=lambda cols: [col.lower() for col in cols],
            schema_overrides=force_to_string
        ).slice(offset=offset, length=chunk_size).select(columns_to_keep)


# Column Manipulations
def clean_addnum_pre_lazy(lazy_frame: pl.LazyFrame, complete_word_replacement_dict: dict) -> pl.LazyFrame:
    """
    Apply transformation rules to clean the `addnum_pre` column in a LazyFrame.
    
    Parameters:
        lazy_frame (pl.LazyFrame): Input LazyFrame containing the columns `addnum_pre`, `add_number`, and `st_predir`.
        complete_word_replacement (dict): Dictionary of word replacements for standardization.
    
    Returns:
        pl.LazyFrame: Transformed LazyFrame with cleaned columns.
    """
    # Define regex patterns
    directional_pattern = r"^(\d+)([NSEW])$"
    invalid_values = {"<NULL", "NULL", "- NULL"}
    removal_patterns = [
        r"^[A-Z]$",  # Single letters
        r"^\d+-\d+$"  # Numbers separated by '-'
    ]
    keywords_to_remove = {"HOUSE", "ANT"}
    valid_terms = {"TRAIL MARKER", "MM", "MILE MARKER", "KIOSK", "EXIT", "BLDG", "BULLBD", "BUILDING", "BILLBOARD"}

    
    # Define transformations using Polars expressions
    cleaned = (
        lazy_frame
        # 1. Check for incorrectly split integer-directional
        .with_columns(
            pl.when(pl.col("addnum_pre").str.contains(directional_pattern))  # 1. Fix incorrectly split integer-directional
            .then(
                pl.struct([
                    pl.lit(""),  # Empty `addnum_pre`
                    (pl.col("addnum_pre") + pl.col("add_number")).alias("add_number"),  # Concatenated value
                    pl.col("st_predir")  # Keep `st_predir`
                ])
            )

            # 2. Move directional words to `st_predir`
            .when(pl.col("addnum_pre").is_in(["EAST", "WEST", "SOUTH", "NORTH"]))
            .then(
                pl.struct([
                    pl.lit(""),  # Empty `addnum_pre`
                    pl.col("add_number"),  # Keep `add_number`
                    pl.when(pl.col("st_predir").is_null())
                    .then(pl.col("addnum_pre"))  # Move to `st_predir` if it's empty
                    .otherwise(pl.col("st_predir"))  # Otherwise, keep existing `st_predir`
                ])
            )
            # 3. Standardize valid terms
            .when(pl.col("addnum_pre").is_in(valid_terms))
            .then(
                pl.struct([
                    pl.when(pl.col("addnum_pre").is_in(complete_word_replacement_dict.keys()))
                    .then(pl.col("addnum_pre").replace(complete_word_replacement_dict))
                    .otherwise(pl.col("addnum_pre")),  # Keep the original value if no match
                    pl.col("add_number"),  # Keep `add_number`
                    pl.col("st_predir")  # Keep `st_predir`
                ])
            )
            # 4. Remove invalid values
            .when(pl.col("addnum_pre").is_in(invalid_values))
            .then(
                pl.struct([
                    pl.lit(""),  # Empty `addnum_pre`
                    pl.col("add_number"),  # Keep `add_number`
                    pl.col("st_predir")  # Keep `st_predir`
                ])
            )
            # 5. Apply regex-based deletions
            .when(
                pl.col("addnum_pre").str.contains("|".join(removal_patterns)) | 
                pl.col("addnum_pre").is_in(keywords_to_remove)
            )
            .then(
                pl.struct([
                    pl.lit(""),  # Empty `addnum_pre`
                    pl.col("add_number"),  # Keep `add_number`
                    pl.col("st_predir")  # Keep `st_predir`
                ])
            )
            # Default: Delete everything else
            .otherwise(
                pl.struct([
                    pl.lit(""),  # Empty `addnum_pre`
                    pl.col("add_number"),  # Keep `add_number`
                    pl.col("st_predir")  # Keep `st_predir`
                ])
            )
            .alias("cleaned")
        )
        # Extract fields from the struct
        .with_columns([
            pl.col("cleaned").struct.field("addnum_pre").alias("addnum_pre"),
            pl.col("cleaned").struct.field("add_number").alias("add_number"),
            pl.col("cleaned").struct.field("st_predir").alias("st_predir")
        ])
        # Drop the temporary struct column
        .drop("cleaned")
    )
    
    return cleaned

def clean_addnum_suf_lazy(lazy_frame: pl.LazyFrame) -> pl.LazyFrame:
    """
    Clean the `addnum_suf` column by:
    - Retaining fractions (1/2, 3/4) and decimals (.1 - .9) in `addnum_suf`
    - Moving only the remaining text to `secondary_address`
    - Moving all non-fraction/decimal values completely to `secondary_address`
    
    Parameters:
        lazy_frame (pl.LazyFrame): Input LazyFrame with `addnum_suf` and `secondary_address`.

    Returns:
        pl.LazyFrame: Transformed LazyFrame with cleaned columns.
    
    Note:
    - This will exclude proper address number suffixes like A.  Most of the values that
        could be proper are actually UNIT, BUILDING, APARTMENT, etc.  Most addresseses 
        are resolveable without these, so they're removed as a rule.
    """

    # Define regex patterns
    fraction_pattern = r'^(1[\\/]2|1[\\/]3|1[\\/]4|2[\\/]3|3[\\/]4)\b'
    decimal_pattern = r'^(?:\.1|\.2|\.3|\.4|\.5|\.6|\.7|\.8|\.9)\b'  

    cleaned = (
        lazy_frame
        # 1. Normalize addnum_suf (replace placeholders with nulls)
        .with_columns(
            pl.when(pl.col("addnum_suf").is_in(["<NULL>", "UNKNOWN", ""]))
            .then(pl.lit(None))
            .otherwise(pl.col("addnum_suf"))
            .alias("addnum_suf")
        )

        # 2. Extract fraction/decimal from addnum_suf
        .with_columns([
            pl.col("addnum_suf").str.extract(fraction_pattern, 1).alias("fraction"),
            pl.col("addnum_suf").str.extract(decimal_pattern, 0).alias("decimal"),
        ])

        # 3. Remove extracted fraction/decimal from addnum_suf
        .with_columns(
            pl.col("addnum_suf")
            .str.replace(fraction_pattern, "", literal=False)
            .str.replace(decimal_pattern, "", literal=False)
            .str.strip_chars()
            .alias("remaining_text")
        )

        # 4. Assign final addnum_suf (keeping only fraction/decimal)
        .with_columns(
            pl.when(pl.col("fraction").is_not_null())
            .then(pl.col("fraction"))
            .when(pl.col("decimal").is_not_null())
            .then(pl.col("decimal"))
            .otherwise(None)
            .alias("addnum_suf")
        )

        # 5. Move remaining text to secondary_address
        .with_columns(
            pl.when(pl.col("remaining_text") != "")
            .then(
                pl.when(pl.col("secondary_address").is_null())
                .then(pl.col("remaining_text"))
                .otherwise(
                    pl.concat_str([pl.col("secondary_address"), pl.col("remaining_text")], separator=" ")
                    .str.strip_chars()
                )
            )
            .otherwise(pl.col("secondary_address"))
            .alias("secondary_address")
        )
        .drop(["fraction", "decimal", "remaining_text"])
    )

    return cleaned

def clean_st_premod_lazy(
    lazy_frame: pl.LazyFrame,
    full_state_name_to_two_digit_state_code: dict,
    st_premod_replacements: dict,
    address_directionals: dict
) -> pl.LazyFrame:
    """
    Clean the `st_premod` column according to specified rules:
    1. Handle special case 'STEPETZ' in Minnesota
    2. Move directional bounds to st_posmod
    3. Move 'FM' to st_pretyp
    4. Remove specified invalid values
    5. Move single letters (A,B,C,D) to secondary_address
    6. Replace full state names with codes
    7. Apply standard replacements
    8. Move directionals to st_predir
    
    Parameters:
        lazy_frame (pl.LazyFrame): Input LazyFrame with address components
        full_state_name_to_two_digit_state_code (dict): Mapping of full state names to codes
        st_premod_replacements (dict): Standard replacements for st_premod values
        address_directionals (dict): Mapping of directional terms to standard forms

    Returns:
        pl.LazyFrame: Transformed LazyFrame with cleaned columns
    """
    
    # Define constants
    directional_bounds = ['NORTHBOUND', 'SOUTHBOUND', 'EASTBOUND', 'WESTBOUND']
    invalid_values = ['<NULL>', '291 -', '703 -', '8', '141-13-1', '1226', '301 -', 
                     '6', 'TOWN', '4', '8133 SPACE', '377 -', '690 -']
    single_letters = ['A', 'B', 'C', 'D']

    cleaned = (
        lazy_frame
        # 1. Handle STEPETZ special case
        .with_columns([
            pl.when((pl.col("st_premod") == "STEPETZ") & (pl.col("state") == "MN"))
            .then(pl.lit(None))
            .otherwise(pl.col("st_premod"))
            .alias("st_premod"),
            
            pl.when((pl.col("st_premod") == "STEPETZ") & (pl.col("state") == "MN"))
            .then(pl.lit(None))
            .otherwise(pl.col("st_predir"))
            .alias("st_predir"),
            
            pl.when((pl.col("st_premod") == "STEPETZ") & (pl.col("state") == "MN"))
            .then(pl.lit(None))
            .otherwise(pl.col("st_pretyp"))
            .alias("st_pretyp"),
            
            pl.when((pl.col("st_premod") == "STEPETZ") & (pl.col("state") == "MN"))
            .then(pl.lit(None))
            .otherwise(pl.col("st_presep"))
            .alias("st_presep"),
            
            pl.when((pl.col("st_premod") == "STEPETZ") & (pl.col("state") == "MN"))
            .then(pl.lit("STEPETZ"))
            .otherwise(pl.col("st_name"))
            .alias("st_name"),
            
            pl.when((pl.col("st_premod") == "STEPETZ") & (pl.col("state") == "MN"))
            .then(pl.lit("ROAD"))
            .otherwise(pl.col("st_postyp"))
            .alias("st_postyp"),
            
            pl.when((pl.col("st_premod") == "STEPETZ") & (pl.col("state") == "MN"))
            .then(pl.lit(None))
            .otherwise(pl.col("st_posdir"))
            .alias("st_posdir"),
            
            pl.when((pl.col("st_premod") == "STEPETZ") & (pl.col("state") == "MN"))
            .then(pl.lit("53"))
            .otherwise(pl.col("st_posmod"))
            .alias("st_posmod")
        ])
        
        # 2. Move directional bounds to st_posmod
        .with_columns([
            pl.when(pl.col("st_premod").is_in(directional_bounds))
            .then(pl.col("st_premod"))
            .otherwise(pl.col("st_posmod"))
            .alias("st_posmod"),
            
            pl.when(pl.col("st_premod").is_in(directional_bounds))
            .then(pl.lit(None))
            .otherwise(pl.col("st_premod"))
            .alias("st_premod")
        ])
        
        # 3. Move FM to st_pretyp
        .with_columns([
            pl.when(pl.col("st_premod") == "FM")
            .then(pl.lit("FM"))
            .otherwise(pl.col("st_pretyp"))
            .alias("st_pretyp"),
            
            pl.when(pl.col("st_premod") == "FM")
            .then(pl.lit(None))
            .otherwise(pl.col("st_premod"))
            .alias("st_premod")
        ])
        
        # 4. Remove invalid values
        .with_columns(
            pl.when(pl.col("st_premod").is_in(invalid_values))
            .then(pl.lit(None))
            .otherwise(pl.col("st_premod"))
            .alias("st_premod")
        )
        
        # 5. Move single letters to secondary_address
        .with_columns([
            pl.when(pl.col("st_premod").is_in(single_letters))
            .then(
                pl.when(pl.col("secondary_address").is_null())
                .then(pl.col("st_premod"))
                .otherwise(
                    pl.concat_str([pl.col("secondary_address"), pl.col("st_premod")], separator=" ")
                    .str.strip_chars()
                )
            )
            .otherwise(pl.col("secondary_address"))
            .alias("secondary_address"),
            
            pl.when(pl.col("st_premod").is_in(single_letters))
            .then(pl.lit(None))
            .otherwise(pl.col("st_premod"))
            .alias("st_premod")
        ])
        
        # 6. Replace full state names with codes
        .with_columns(
            pl.col("st_premod").replace(full_state_name_to_two_digit_state_code)
            .alias("st_premod")
        )
        
        # 7. Apply standard replacements
        .with_columns(
            pl.col("st_premod").replace(st_premod_replacements)
            .alias("st_premod")
        )
        
        # 8. Move directionals to st_predir
        .with_columns([
            pl.when(pl.col("st_premod").is_in(address_directionals.keys()))
            .then(pl.col("st_premod").replace(address_directionals))
            .otherwise(pl.col("st_predir"))
            .alias("st_predir"),
            
            pl.when(pl.col("st_premod").is_in(address_directionals.keys()))
            .then(pl.lit(None))
            .otherwise(pl.col("st_premod"))
            .alias("st_premod")
        ])
    )
    
    return cleaned

def clean_st_predir_lazy(lazy_frame: pl.LazyFrame) -> pl.LazyFrame:
    """
    Clean the `st_predir` column by removing specified invalid values.
    
    Parameters:
        lazy_frame (pl.LazyFrame): Input LazyFrame with address components

    Returns:
        pl.LazyFrame: Transformed LazyFrame with cleaned st_predir column
    """
    
    # Define invalid values that should be removed
    invalid_values = ['PULASKI', 'ATTU STATI', '13TDE96951', 'JONES', 'UNKNOWN']

    cleaned = (
        lazy_frame
        .with_columns(
            pl.when(pl.col("st_predir").is_in(invalid_values))
            .then(pl.lit(None))
            .otherwise(pl.col("st_predir"))
            .alias("st_predir")
        )
    )
    
    return cleaned

def clean_st_pretyp_lazy(
    lazy_frame: pl.LazyFrame,
    st_pretyp_replacements: dict
) -> pl.LazyFrame:
    """
    Clean the `st_pretyp` column by:
    1. Removing 'UNKNOWN' and 'UNK' values
    2. Replacing values according to st_pretyp_replacements dictionary
    
    Parameters:
        lazy_frame (pl.LazyFrame): Input LazyFrame with address components
        st_pretyp_replacements (dict): Dictionary mapping values to their replacements

    Returns:
        pl.LazyFrame: Transformed LazyFrame with cleaned st_pretyp column
    
    Example:
        If st_pretyp contains: ['UNKNOWN', 'UNK', 'ABY', 'FRED']
        and st_pretyp_replacements is {'ABY':'ABBEY'}
        Result will be: [null, null, 'ABBEY', 'FRED']
    """
    
    # Define invalid values that should be removed
    invalid_values = ['UNKNOWN', 'UNK']

    cleaned = (
        lazy_frame
        # First remove invalid values
        .with_columns(
            pl.when(pl.col("st_pretyp").is_in(invalid_values))
            .then(pl.lit(None))
            .otherwise(pl.col("st_pretyp"))
            .alias("st_pretyp")
        )
        # Then apply replacements from dictionary
        .with_columns(
            pl.col("st_pretyp").replace(st_pretyp_replacements)
            .alias("st_pretyp")
        )
    )
    
    return cleaned

def clean_st_name_lazy(
    lazy_frame: pl.LazyFrame,
    complete_word_replacement_dict: dict,
    usps_st_posttyp: list,
    address_directionals: dict,
    list_of_address_directionals: list
) -> pl.LazyFrame:
    """
    Clean the street name column by:
    - Cleaning strings using clean_string()
    - Standardizing words using city_name_standardize_whole_words()
    - Moving street types to st_postyp column
    - Moving pre-directionals to st_predir
    - Moving post-directionals to st_posdir
    - Moving unit number patterns to secondary_address
    
    Parameters:
        lazy_frame (pl.LazyFrame): Input LazyFrame with 'st_name' column
        complete_word_replacement_dict (dict): Dictionary of misspelled words and their corrections
        usps_st_posttyp (list): Valid street post types per USPS
        address_directionals (dict): Directional abbreviations and full words
        list_of_address_directionals (list): Valid address directionals
        
    Returns:
        pl.LazyFrame: Transformed LazyFrame with cleaned street names
    """
    unit_pattern = re.compile(r"[A-Za-z]*\s?\d+\s?[-~/\\]\s?[A-Za-z]*\s?\d+")
    
    def move_street_type(row: dict) -> dict:
        st_name = row["st_name"]
        st_postyp = row["st_postyp"]
        
        if not st_name:
            return {"st_name": st_name, "st_postyp": st_postyp}
            
        words = st_name.split()
        
        if st_postyp is not None:
            if words[-1] == st_postyp:
                return {"st_name": " ".join(words[:-1]), "st_postyp": st_postyp}
        
        post_type_indices = [i for i, word in enumerate(words) if word in usps_st_posttyp]
        if not post_type_indices:
            return {"st_name": st_name, "st_postyp": st_postyp}
        
        idx = post_type_indices[-1]
        if st_postyp is None:
            new_postyp = words[idx]
        else:
            new_postyp = st_postyp  
        
        new_name = ' '.join(words[:idx] + words[idx + 1:])
        return {"st_name": new_name, "st_postyp": new_postyp}
    
    def move_directionals(row: dict) -> dict:
        st_name = row["st_name"]
        st_predir = row["st_predir"]
        st_posdir = row["st_posdir"]
        
        if not st_name:
            return {"st_name": st_name, "st_predir": st_predir, "st_posdir": st_posdir}
        
        words = st_name.split()
        
        if len(words) > 1 and words[0] in list_of_address_directionals:
            if st_predir is None:
                st_predir = words[0]
                words = words[1:]
            else:
                words = words[1:]
        
        if len(words) > 1 and words[-1] in list_of_address_directionals:
            if st_posdir is None:
                st_posdir = words[-1]
                words = words[:-1]
            else:
                words = words[:-1]
        
        return {"st_name": " ".join(words), "st_predir": st_predir, "st_posdir": st_posdir}
    
    def move_unit_numbers(row: dict) -> dict:
        st_name = row["st_name"]
        secondary_address = row.get("secondary_address", None)
        
        if not st_name:
            return {"st_name": st_name, "secondary_address": secondary_address}
        
        matches = unit_pattern.findall(st_name)
        if matches:
            for match in matches:
                if secondary_address is None:
                    secondary_address = match  # If secondary_address is None, set it to match
                elif match not in secondary_address:
                    secondary_address = (secondary_address + " " + match).strip()
            st_name = st_name.replace(match, "").strip()  # Remove the match from st_name

        return {"st_name": st_name, "secondary_address": secondary_address}
    
    
    cleaned = (
        lazy_frame
        .with_columns(
            pl.col("st_name").map_elements(clean_string, return_dtype=pl.Utf8).alias("st_name")
        )
        .with_columns(
            pl.col("st_name")
            .map_elements(
                lambda x: city_name_standardize_whole_words(x, complete_word_replacement_dict),
                return_dtype=pl.Utf8
            )
            .alias("st_name")
        )
        .with_columns(
            pl.struct(["st_name", "st_postyp"])
            .map_elements(
                move_street_type,
                return_dtype=pl.Struct([pl.Field("st_name", pl.Utf8), pl.Field("st_postyp", pl.Utf8)])
            )
            .alias("result")
        )
        .with_columns([
            pl.col("result").struct.field("st_name").alias("st_name"),
            pl.col("result").struct.field("st_postyp").alias("st_postyp")
        ])
        .drop("result")
        .with_columns(
            pl.struct(["st_name", "st_predir", "st_posdir"])
            .map_elements(
                move_directionals,
                return_dtype=pl.Struct([
                    pl.Field("st_name", pl.Utf8),
                    pl.Field("st_predir", pl.Utf8),
                    pl.Field("st_posdir", pl.Utf8)
                ])
            )
            .alias("result")
        )
        .with_columns([
            pl.col("result").struct.field("st_name").alias("st_name"),
            pl.col("result").struct.field("st_predir").alias("st_predir"),
            pl.col("result").struct.field("st_posdir").alias("st_posdir")
        ])
        .drop("result")
        .with_columns(
            pl.struct(["st_name", "secondary_address"])
            .map_elements(
                move_unit_numbers,
                return_dtype=pl.Struct([
                    pl.Field("st_name", pl.Utf8),
                    pl.Field("secondary_address", pl.Utf8)
                ])
            )
            .alias("result")
        )
        .with_columns([
            pl.col("result").struct.field("st_name").alias("st_name"),
            pl.col("result").struct.field("secondary_address").alias("secondary_address")
        ])
        .drop("result")
    )
    return cleaned

def clean_st_posdir_lazy(lazy_frame: pl.LazyFrame) -> pl.LazyFrame:
    """
    Clean the `st_posdir` column by removing specified invalid values.
    
    Parameters:
        lazy_frame (pl.LazyFrame): Input LazyFrame with address components

    Returns:
        pl.LazyFrame: Transformed LazyFrame with cleaned st_posdir column
    """
    
    # Define invalid values that should be removed
    invalid_values = ['IA', 'ATTU STATI']

    cleaned = (
        lazy_frame
        .with_columns(
            pl.when(pl.col("st_posdir").is_in(invalid_values))
            .then(pl.lit(None))
            .otherwise(pl.col("st_posdir"))
            .alias("st_posdir")
        )
    )
    
    return cleaned

def clean_st_posmod_lazy(lazy_frame: pl.LazyFrame) -> pl.LazyFrame:
    """
    Clean the st_posmod column by:
    - Removing numeric or hyphenated numeric values
    - Removing st_posmod values that match post_city exactly
    - Removing st_posmod values that are in a specific list
    - Moving 'EAST CAROGA' to st_name
    - Moving 'UPSTAIRS' to secondary_address
    - Overwriting post_city in special conditions
    - Handling specific cases for certain values of st_posmod
    
    Parameters:
        lazy_frame (pl.LazyFrame): Input LazyFrame with columns including st_posmod, post_city, etc.
        
    Returns:
        pl.LazyFrame: Transformed LazyFrame with cleaned st_posmod column
    """
    
    # List of values to remove from st_posmod
    list_to_remove = [
        'EDGEWATR C', 'EDGEWATR B', 'EDGEWATR D', 'PECK LAKE', 'BEAUFORT', 'EDGEWATR A', 
        'EDGEWATR E', 'RODMAN', 'HARDING PK', 'CSL', 'MALBA', 'DOUGLASTON', 'ROCKAWAYS', 
        '-OFF', 'MHP', 'ERWIN', '7882 FRIENDSHIP RD', '2598 HWY 131', 'JOE SIMMONS', 
        '103 UNICORN LN', 'SILVER BAY', 'PAYPHONE', '7648 OAK GROVE RD', 'PRLOT', 
        '7748 MULBERRY GAP RD', '280 YELLOWSTONE RD', 'SHEFFIELD LN', '<NULL>', 
        '617 JOHNNY STIEFEL D'
    ]
    
    # Helper function to check if a string is numeric or a hyphenated number
    def is_numeric_or_hyphenated(value: str) -> bool:
        return bool(re.fullmatch(r"[-]?\d+", value.strip()))  # Check for numeric or hyphenated numbers
    
    # Step 1: Remove numeric or hyphenated values from st_posmod
    def clean_posmod(row: dict) -> dict:
        st_posmod = row.get("st_posmod", None)
        if st_posmod and is_numeric_or_hyphenated(st_posmod):
            st_posmod = None
        return {"st_posmod": st_posmod}
    
    # Step 2: Remove st_posmod if it matches post_city
    def match_post_city(row: dict) -> dict:
        st_posmod = row.get("st_posmod", None)
        post_city_val = row.get("post_city", None)
        if st_posmod and post_city_val and st_posmod.strip().upper() == post_city_val.strip().upper():
            st_posmod = None
        return {"st_posmod": st_posmod}

    # Step 3: Remove st_posmod if it is in the list of values
    def remove_from_list(row: dict) -> dict:
        st_posmod = row.get("st_posmod", None)
        if st_posmod and st_posmod.strip() in list_to_remove:
            st_posmod = None
        return {"st_posmod": st_posmod}

    # Step 4: Move 'EAST CAROGA' to st_name and delete st_posmod
    def move_east_caroga(row: dict) -> dict:
        st_posmod = row.get("st_posmod", None)
        st_name = row.get("st_name", None)
        if st_posmod == "EAST CAROGA":
            if st_name:
                st_name = f"{st_name} EAST CAROGA"
            else:
                st_name = "EAST CAROGA"
            st_posmod = None
        return {"st_name": st_name, "st_posmod": st_posmod}

    # Step 5: Move 'UPSTAIRS' to secondary_address and delete st_posmod
    def move_upstairs(row: dict) -> dict:
        st_posmod = row.get("st_posmod", None)
        secondary_address = row.get("secondary_address", None)
        if st_posmod == "UPSTAIRS":
            if secondary_address:
                secondary_address = f"{secondary_address} UPSTAIRS"
            else:
                secondary_address = "UPSTAIRS"
            st_posmod = None
        return {"st_posmod": st_posmod, "secondary_address": secondary_address}
    
    # Step 6: Overwrite post_city if st_posmod is in certain list and state is KY
    def handle_special_ky(row: dict) -> dict:
        st_posmod = row.get("st_posmod", None)
        post_city = row.get("post_city", None)
        state = row.get("state", None)
        if st_posmod in ['MAZIE', 'ADAMS', 'LOUISA', 'CATLETTSBURG'] and post_city == 'NOT STATED' and state == 'KY':
            post_city = st_posmod
            st_posmod = None
        return {"st_posmod": st_posmod, "post_city": post_city}
    
    # Step 7: Overwrite post_city if st_posmod = '(TAUNTON)' and state is MA
    def handle_taunton(row: dict) -> dict:
        st_posmod = row.get("st_posmod", None)
        post_city = row.get("post_city", None)
        state = row.get("state", None)
        if st_posmod == "(TAUNTON)" and state == "MA" and post_city == "NOT STATED":
            post_city = "TAUNTON"
            st_posmod = None
        return {"st_posmod": st_posmod, "post_city": post_city}

    # Step 8: Overwrite post_city if st_posmod = 'ROYAL LAKES' and state is IL
    def handle_royal_lakes(row: dict) -> dict:
        st_posmod = row.get("st_posmod", None)
        post_city = row.get("post_city", None)
        state = row.get("state", None)
        if st_posmod == "ROYAL LAKES" and state == "IL" and post_city == "NOT STATED":
            post_city = "ROYAL LAKES"
            st_posmod = None
        return {"st_posmod": st_posmod, "post_city": post_city}

    # Step 9: Overwrite st_name and st_postyp for specific st_posmod values
    def handle_oil_field(row: dict) -> dict:
        st_posmod = row.get("st_posmod", None)
        st_name = row.get("st_name", None)
        st_postyp = row.get("st_postyp", None)
        if st_posmod in ['OIL FIELD ROAD PRIVATE RO', 'OIL FIELD ROAD', 
                         'OIL FIELD ROAD A PRIVATE', 'OIL FIELD ROAD B PRIVATE']:
            st_name = 'OIL FIELD'
            st_postyp = 'ROAD'
            st_posmod = None
        return {"st_posmod": st_posmod, "st_name": st_name, "st_postyp": st_postyp}
    
    cleaned = (
        lazy_frame
        .with_columns(
            pl.struct(["st_posmod"])
            .map_elements(clean_posmod, return_dtype=pl.Struct([pl.Field("st_posmod", pl.Utf8)]))
            .alias("result")
        )
        .with_columns([
            pl.col("result").struct.field("st_posmod").alias("st_posmod")
        ])
        .drop("result")
        .with_columns(
            pl.struct(["st_posmod", "post_city"])
            .map_elements(match_post_city, return_dtype=pl.Struct([pl.Field("st_posmod", pl.Utf8)]))
            .alias("result")
        )
        .with_columns([
            pl.col("result").struct.field("st_posmod").alias("st_posmod")
        ])
        .drop("result")
        .with_columns(
            pl.struct(["st_posmod"])
            .map_elements(remove_from_list, return_dtype=pl.Struct([pl.Field("st_posmod", pl.Utf8)]))
            .alias("result")
        )
        .with_columns([
            pl.col("result").struct.field("st_posmod").alias("st_posmod")
        ])
        .drop("result")
        .with_columns(
            pl.struct(["st_name", "st_posmod"])
            .map_elements(move_east_caroga, return_dtype=pl.Struct([pl.Field("st_name", pl.Utf8), pl.Field("st_posmod", pl.Utf8)]))
            .alias("result")
        )
        .with_columns([
            pl.col("result").struct.field("st_name").alias("st_name"),
            pl.col("result").struct.field("st_posmod").alias("st_posmod")
        ])
        .drop("result")
        .with_columns(
            pl.struct(["st_posmod", "secondary_address"])
            .map_elements(move_upstairs, return_dtype=pl.Struct([pl.Field("st_posmod", pl.Utf8), pl.Field("secondary_address", pl.Utf8)]))
            .alias("result")
        )
        .with_columns([
            pl.col("result").struct.field("st_posmod").alias("st_posmod"),
            pl.col("result").struct.field("secondary_address").alias("secondary_address")
        ])
        .drop("result")
        .with_columns(
            pl.struct(["st_posmod", "post_city", "state"])
            .map_elements(handle_special_ky, return_dtype=pl.Struct([pl.Field("st_posmod", pl.Utf8), pl.Field("post_city", pl.Utf8)]))
            .alias("result")
        )
        .with_columns([
            pl.col("result").struct.field("st_posmod").alias("st_posmod"),
            pl.col("result").struct.field("post_city").alias("post_city")
        ])
        .drop("result")
        .with_columns(
            pl.struct(["st_posmod", "post_city", "state"])
            .map_elements(handle_taunton, return_dtype=pl.Struct([pl.Field("st_posmod", pl.Utf8), pl.Field("post_city", pl.Utf8)]))
            .alias("result")
        )
        .with_columns([
            pl.col("result").struct.field("st_posmod").alias("st_posmod"),
            pl.col("result").struct.field("post_city").alias("post_city")
        ])
        .drop("result")
        .with_columns(
            pl.struct(["st_posmod", "post_city", "state"])
            .map_elements(handle_royal_lakes, return_dtype=pl.Struct([pl.Field("st_posmod", pl.Utf8), pl.Field("post_city", pl.Utf8)]))
            .alias("result")
        )
        .with_columns([
            pl.col("result").struct.field("st_posmod").alias("st_posmod"),
            pl.col("result").struct.field("post_city").alias("post_city")
        ])
        .drop("result")
        .with_columns(
            pl.struct(["st_posmod", "st_name", "st_postyp"])
            .map_elements(handle_oil_field, return_dtype=pl.Struct([pl.Field("st_posmod", pl.Utf8), pl.Field("st_name", pl.Utf8), pl.Field("st_postyp", pl.Utf8)]))
            .alias("result")
        )
        .with_columns([
            pl.col("result").struct.field("st_posmod").alias("st_posmod"),
            pl.col("result").struct.field("st_name").alias("st_name"),
            pl.col("result").struct.field("st_postyp").alias("st_postyp")
        ])
        .drop("result")
    )
    
    return cleaned

# Pipeline
# Main processing function
def process_nad_file(input_file: str, output_file: str, batch_size: int) -> None:
    """
    Process a large address file in chunks, applying transformations and combining results.
    
    This function handles the end-to-end processing of address data by:
    1. Determining optimal processing parameters based on system resources
    2. Loading and transforming data in chunks
    3. Creating derived fields (secondary_address, full_address)
    4. Saving intermediate results as parquet files
    5. Combining results into a final output file
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path where the final parquet file should be saved
        batch_size (int): Initial batch size for processing chunks
        
    Side Effects:
        - Creates temporary parquet files during processing
        - Writes final output to specified parquet file
        - Logs progress and status information
        - Cleans up temporary files after processing
    """
    # Initialize logging for the processing session
    logger = setup_logging()

    # Determine optimal processing parameters based on system resources
    logger.info("Calculating optimal batch size based on available system resources...")
    batch_size = calculate_optimal_batch_size(batch_size)

    # Log available computational resources
    cpus_available = multiprocessing.cpu_count()
    logger.info(f"Available CPUs: {cpus_available}")
    
    # Initialize tracking for chunk processing
    iteration = 0
    chunk_files = []  # Track temporary chunk files for later cleanup
    
    # Process each chunk of the input file
    for lazy_chunk in create_lazy_chunks(input_file, batch_size):
        # Apply standard cleaning to all columns
        lazy_chunk = lazy_chunk.with_columns(
            [transform_column(col) for col in lazy_chunk.collect_schema().names()]
        )

        # Create secondary_address from component fields
        columns_to_process = ["building", "floor", "unit", "room", "seat"]
        secondary_address_expr = pl.concat_str(
            [
                pl.when(pl.col(col).is_not_null() & (pl.col(col).str.strip_chars() != ""))
                .then(pl.lit(col.upper()).str.strip_chars() + pl.lit(" ") + 
                      pl.col(col).str.to_uppercase().str.strip_chars())
                .otherwise(None)
                for col in columns_to_process
            ],
            separator=" ",
            ignore_nulls=True
        ).map_elements(
            lambda x: None if x == "" else x, 
            return_dtype=pl.Utf8
        ).alias("secondary_address")
        
        lazy_chunk = lazy_chunk.with_columns([secondary_address_expr])
        
        # Create full_address by combining all address components
        full_address_expr = (
            pl.concat_str(
                [
                    pl.col("addno_full").fill_null("").str.strip_chars(),
                    pl.lit(" "),
                    pl.col("stnam_full").fill_null("").str.strip_chars(),
                    pl.when(pl.col("secondary_address").fill_null("").str.strip_chars() != "")
                    .then(pl.concat_str([pl.lit(" "), 
                          pl.col("secondary_address").fill_null("").str.strip_chars()], 
                          separator=""))
                    .otherwise(pl.lit("")),
                    pl.lit(", "),
                    pl.col("post_city").fill_null("").str.strip_chars(),
                    pl.lit(", "),
                    pl.col("state").fill_null("").str.strip_chars(),
                    pl.lit(" "),
                    pl.col("zip_code").fill_null("").str.strip_chars(),
                ],
                separator="",
            )
            .str.replace_all(r"\s+", " ")
            .str.strip_chars()
            .alias("full_address")
        )
        lazy_chunk = lazy_chunk.with_columns([full_address_expr])

        # Apply cleaning functions to specific columns
        lazy_chunk = clean_addnum_pre_lazy(lazy_chunk, complete_word_replacement_dict)
        lazy_chunk = clean_addnum_suf_lazy(lazy_chunk)
        lazy_chunk = clean_st_premod_lazy(lazy_chunk, full_state_name_to_two_digit_state_code, st_premod_replacements, address_directionals)
        lazy_chunk = clean_st_predir_lazy(lazy_chunk)
        lazy_chunk = clean_st_pretyp_lazy(lazy_chunk, st_pretyp_replacements)
        lazy_chunk = clean_st_name_lazy(lazy_chunk, complete_word_replacement_dict, usps_st_posttyp, address_directionals, list_of_address_directionals)
        lazy_chunk = clean_st_posdir_lazy(lazy_chunk)
        lazy_chunk = clean_st_posmod_lazy(lazy_chunk)
        
        # Materialize the chunk and remove processed component columns
        chunk_df = lazy_chunk.drop(
            'building', 'floor', 'unit', 'room', 'seat', 'addno_full', 'stnam_full'
        ).collect()
        
        # Save chunk to temporary parquet file
        chunk_file = f"chunk_{iteration}.parquet"
        chunk_df.write_parquet(chunk_file, compression="zstd")
        chunk_files.append(chunk_file)

        # Clean up memory after processing chunk
        gc.collect()
        iteration += 1
        
    # Combine all processed chunks into final output file
    logger.info("Combining all chunks into a single Parquet file...")
    combined_df = pl.concat(
        [pl.scan_parquet(chunk_file) for chunk_file in chunk_files]
    ).collect()
    combined_df.write_parquet(output_file, compression="zstd")

    # Clean up temporary files
    logger.info("Cleaning up temporary chunk files...")
    for chunk_file in chunk_files:
        os.remove(chunk_file)

    logger.info("Processing complete.")


def extract_address_data(nad_input_file: str, nad_output_file: str, batch_size: int = 5_000_000, regenerate: bool = False):
    """
    Extracts and processes address data from the NAD file, handling file existence and regeneration.

    Args:
        nad_input_file: Path to the input NAD text file.
        nad_output_file: Path to save the output Parquet file.
        batch_size: The number of rows to process in each batch.
        regenerate: Whether to regenerate the file if it already exists.
    """
    if not regenerate and os.path.exists(nad_output_file):
        try:
            pq.ParquetFile(nad_output_file)  # Just try to open; no data read
            print("National Address Database output file already exists.")
            return  # File exists, is a valid Parquet, and regenerate is False
        except Exception:
            pass # Not a valid Parquet, continue to regenerate

    if os.path.exists(nad_output_file):
        os.remove(nad_output_file)  # Delete existing file if conditions are not met

    process_nad_file(nad_input_file, nad_output_file, batch_size)

