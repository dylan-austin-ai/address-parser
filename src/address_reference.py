"""
Reference data for address normalization and validation.
Contains state codes, directionals, USPS street types, and correction dictionaries.
"""

from typing import Dict, List

# 1.2 State Reference
STATE_CODES: List[str] = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"
]

FULL_STATE_NAME_TO_TWO_DIGIT_STATE_CODE: Dict[str, str] = {
    "ALABAMA": "AL", "ALASKA": "AK", "ARIZONA": "AZ", "ARKANSAS": "AR", "CALIFORNIA": "CA", "COLORADO": "CO", "CONNECTICUT": "CT",
    "DELAWARE": "DE", "FLORIDA": "FL", "GEORGIA": "GA", "HAWAII": "HI", "IDAHO": "ID", "ILLINOIS": "IL", "INDIANA": "IN",
    "IOWA": "IA", "KANSAS": "KS", "KENTUCKY": "KY", "LOUISIANA": "LA", "MAINE": "ME", "MARYLAND": "MD", "MASSACHUSETTS": "MA",
    "MICHIGAN": "MI", "MINNESOTA": "MN", "MISSISSIPPI": "MS", "MISSOURI": "MO", "MONTANA": "MT", "NEBRASKA": "NE", "NEVADA": "NV",
    "NEW HAMPSHIRE": "NH", "NEW JERSEY": "NJ", "NEW MEXICO": "NM", "NEW YORK": "NY", "NORTH CAROLINA": "NC", "NORTH DAKOTA": "ND",
    "OHIO": "OH", "OKLAHOMA": "OK", "OREGON": "OR", "PENNSYLVANIA": "PA", "RHODE ISLAND": "RI", "SOUTH CAROLINA": "SC",
    "SOUTH DAKOTA": "SD", "TENNESSEE": "TN", "TEXAS": "TX", "UTAH": "UT", "VERMONT": "VT", "VIRGINIA": "VA", "WASHINGTON": "WA",
    "WEST VIRGINIA": "WV", "WISCONSIN": "WI", "WYOMING": "WY", "DISTRICT OF COLUMBIA": "DC"
}

FULL_STATE_NAME_VARIATIONS: Dict[str, str] = {
    "ALA": "AL", "ARK": "AR", "ALAB": "AL", "CONN": "CT", "CALIF": "CA", "CALI": "CA", "N DAKOTA": "ND", "NO DAKOTA": "ND",
    "NORT DAKOTA": "ND", "BLUEGRASS STATE": "KY", "GOLDEN STATE": "CA", "LONE STAR STATE": "TX", "WASH D C": "DC",
    "WASHINGTON DC": "DC", "WASHINGTON D C": "DC"
}

# 1.2 Directional Reference
ADDRESS_DIRECTIONALS: Dict[str, str] = {
    "N": "NORTH", "S": "SOUTH", "E": "EAST", "W": "WEST",
    "NW": "NORTHWEST", "SW": "SOUTHWEST", "NE": "NORTHEAST", "SE": "SOUTHEAST",
    "NNW": "NORTH NORTHWEST", "NNE": "NORTH NORTHEAST", "SSW": "SOUTH SOUTHWEST",
    "SSE": "SOUTH SOUTHEAST", "WNW": "WEST NORTHWEST", "WSW": "WEST SOUTHWEST",
    "ENE": "EAST NORTHEAST", "ESE": "EAST SOUTHEAST"
}

LIST_OF_ADDRESS_DIRECTIONALS: List[str] = list(ADDRESS_DIRECTIONALS.values())

BOUND_DIRECTIONAL_DICT: Dict[str, str] = {
    "NB": "NORTHBOUND", "SB": "SOUTHBOUND", "EB": "EASTBOUND", "WB": "WESTBOUND"
}

# 1.2 USPS Street Type Reference
USPS_ST_POSTTYP: List[str] = [
    "AVE", "BLVD", "CIR", "CT", "DR", "LN", "PKWY", "PL", "RD", "ST", "TER", "WAY"
]

# 1.2 City Name Correction Dictionaries
SUFFIX_SUBSTRING_DICT: Dict[str, str] = {
    "VLE": "VILLE", "TN": "TON", "BG": "BURG", "CHESTR": "CHESTER", 
    "FLD": "FIELD", "LND": "LAND"
}

COMPLETE_WORD_REPLACEMENT_DICT: Dict[str, str] = {
    "GRN": "GREEN", "HGTS": "HEIGHTS", "MTN": "MOUNTAIN",
    "BLMNGTON": "BLOOMINGTON", "CHARLOTTEVLE": "CHARLOTTESVILLE",
    "AFB": "AIR FORCE BASE", "NAS": "NAVAL AIR STATION",
    "NW": "NORTHWEST", "NE": "NORTHEAST", "SW": "SOUTHWEST", "SE": "SOUTHEAST"
}

COMPOUND_WORD_CORRECTIONS_DICT: Dict[tuple, str] = {
    ("BLOOM", "FIELD"): "BLOOMFIELD",
    ("RIVER", "SIDE"): "RIVERSIDE",
    ("WOOD", "LAND"): "WOODLAND"
}

MULTI_WORD_REPLACEMENT_DICT: Dict[str, str] = {
    "WINSTON SALEM": "WINSTON-SALEM",
    "FUQUAY VARINA": "FUQUAY-VARINA",
    "GREEN ACRES": "GREENACRES",
    "COCONUTCREEK": "COCONUT CREEK",
    "FT SM HOUSTON": "FORT SAM HOUSTON"
}

# Fixed duplicate key issues from original report
STATE_SPECIFIC_REPLACEMENTS: Dict[str, Dict[str, str]] = {
    "FL": {"NEW POINT RICHEY": "NEW PORT RICHEY"},
    "PA": {"KING OF PRUSSA": "KING OF PRUSSIA"},
    "TX": {"ROSE CITY": "ROYSE CITY"},
    "MO": {"MOORESVILLE": "MOOREVILLE"},
    "NE": {"LAVISTA": "LA VISTA", "PRAGUE": "SPRAGUE", "WHITE CLAY": "WHITECLAY"}
}

# 1.2 Street Component Correction Dictionaries
ST_PREMOD_REPLACEMENTS: Dict[str, str] = {
    "I": "INTERSTATE", "NYS": "NEW YORK STATE"
}

ST_PRETYP_REPLACEMENTS: Dict[str, str] = {
    "HWY": "HIGHWAY", "BLVD": "BOULEVARD", "RD": "ROAD", "ST": "STREET"
}