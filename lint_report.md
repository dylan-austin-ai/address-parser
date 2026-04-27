# Lint Report

F601 Dictionary key literal `"MOORESVILLE"` repeated (`"MOORESVILLE"` hashes to the same value as `'MOORESVILLE'`)
  --> projects/address-parser/src/address_reference.py:69:181
   |
67 | …LASS':'DOUGLAS', 'FAIR HAVEN':'FAIRHAVEN', 'FAIRPLAIN':'FAIR PLAIN', 'GROSSE POINT FRM':'GROSSE POINTE FARMS', 'GROSSE POINTE FRM':'G…
68 | …CH', 'MINETONKA MILLS': 'MINNETONKA MILLS', 'NEW FOLDEN': 'NEWFOLDEN', 'PARKE': 'PARKER', 'REDLAKE': 'RED LAKE', 'STONY BROOK': 'STON…
69 | …G': 'SLATE SPRINGS', 'SNOW LAKE SHORE': 'SNOW LAKE SHORES', "MOORESVILLE":"MOOREVILLE"}
   |                                                              ^^^^^^^^^^^^^
70 | …RADO SPRINGS',  'EXCELSIOR SPRING': 'EXCELSIOR SPRINGS', 'GREEN CASTLE': 'GREENCASTLE', 'HALF WAY': 'HALFWAY', 'LA BARQUE CREEK': 'LA…
71 | …
   |
help: Remove repeated key literal `"MOORESVILLE"`

F601 Dictionary key literal `"NE"` repeated
  --> projects/address-parser/src/address_reference.py:72:4
   |
70 |     , 'MO': {'ELM DORADO SPRING': 'EL DORADO SPRINGS', 'ELM DORADO SPRINGS':'EL DORADO SPRINGS', 'EL DORADO SPRING': 'EL DORADO SPRING…
71 |     , "MT": {'HERRON': 'HERON'}
72 |     , "NE": {'LAVISTA': 'LA VISTA', 'PRAGUE': 'SPRAGUE', 'WHITE CLAY': 'WHITECLAY'}
   |       ^^^^
73 |     , "NV": {'MOUNTAIN SPRING': 'MOUNTAIN SPRINGS'}
74 |     , "NH": {'WEST PETERBORO': 'WEST PETERBOROUGH'}
   |
help: Remove repeated key literal `"NE"`

E402 Module level import not at top of file
  --> projects/address-parser/src/pre_processing_nad_elements.py:28:1
   |
27 | # Import the modules
28 | from address.address_functions import *
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
29 | from address.address_reference import *
30 | from address.united_states_zipcodes_functions import *
   |

F403 `from address.address_functions import *` used; unable to detect undefined names
  --> projects/address-parser/src/pre_processing_nad_elements.py:28:1
   |
27 | # Import the modules
28 | from address.address_functions import *
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
29 | from address.address_reference import *
30 | from address.united_states_zipcodes_functions import *
   |

E402 Module level import not at top of file
  --> projects/address-parser/src/pre_processing_nad_elements.py:29:1
   |
27 | # Import the modules
28 | from address.address_functions import *
29 | from address.address_reference import *
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
30 | from address.united_states_zipcodes_functions import *
31 | from address.national_address_database_functions import *
   |

F403 `from address.address_reference import *` used; unable to detect undefined names
  --> projects/address-parser/src/pre_processing_nad_elements.py:29:1
   |
27 | # Import the modules
28 | from address.address_functions import *
29 | from address.address_reference import *
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
30 | from address.united_states_zipcodes_functions import *
31 | from address.national_address_database_functions import *
   |

E402 Module level import not at top of file
  --> projects/address-parser/src/pre_processing_nad_elements.py:30:1
   |
28 | from address.address_functions import *
29 | from address.address_reference import *
30 | from address.united_states_zipcodes_functions import *
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
31 | from address.national_address_database_functions import *
   |

F403 `from address.united_states_zipcodes_functions import *` used; unable to detect undefined names
  --> projects/address-parser/src/pre_processing_nad_elements.py:30:1
   |
28 | from address.address_functions import *
29 | from address.address_reference import *
30 | from address.united_states_zipcodes_functions import *
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
31 | from address.national_address_database_functions import *
   |

E402 Module level import not at top of file
  --> projects/address-parser/src/pre_processing_nad_elements.py:31:1
   |
29 | from address.address_reference import *
30 | from address.united_states_zipcodes_functions import *
31 | from address.national_address_database_functions import *
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
32 |
33 | # Helper Functions
   |

F403 `from address.national_address_database_functions import *` used; unable to detect undefined names
  --> projects/address-parser/src/pre_processing_nad_elements.py:31:1
   |
29 | from address.address_reference import *
30 | from address.united_states_zipcodes_functions import *
31 | from address.national_address_database_functions import *
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
32 |
33 | # Helper Functions
   |

F405 `clean_string` may be undefined, or defined from star imports
   --> projects/address-parser/src/pre_processing_nad_elements.py:668:44
    |
666 |         lazy_frame
667 |         .with_columns(
668 |             pl.col("st_name").map_elements(clean_string, return_dtype=pl.Utf8).alias("st_name")
    |                                            ^^^^^^^^^^^^
669 |         )
670 |         .with_columns(
    |

F405 `city_name_standardize_whole_words` may be undefined, or defined from star imports
   --> projects/address-parser/src/pre_processing_nad_elements.py:673:27
    |
671 |             pl.col("st_name")
672 |             .map_elements(
673 |                 lambda x: city_name_standardize_whole_words(x, complete_word_replacement_dict),
    |                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
674 |                 return_dtype=pl.Utf8
675 |             )
    |

F405 `complete_word_replacement_dict` may be undefined, or defined from star imports
    --> projects/address-parser/src/pre_processing_nad_elements.py:1061:56
     |
1060 | …     # Apply cleaning functions to specific columns
1061 | …     lazy_chunk = clean_addnum_pre_lazy(lazy_chunk, complete_word_replacement_dict)
     |                                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1062 | …     lazy_chunk = clean_addnum_suf_lazy(lazy_chunk)
1063 | …     lazy_chunk = clean_st_premod_lazy(lazy_chunk, full_state_name_to_two_digit_state_code, st_premod_replacements, address_directi…
     |

F405 `full_state_name_to_two_digit_state_code` may be undefined, or defined from star imports
    --> projects/address-parser/src/pre_processing_nad_elements.py:1063:55
     |
1061 | …     lazy_chunk = clean_addnum_pre_lazy(lazy_chunk, complete_word_replacement_dict)
1062 | …     lazy_chunk = clean_addnum_suf_lazy(lazy_chunk)
1063 | …     lazy_chunk = clean_st_premod_lazy(lazy_chunk, full_state_name_to_two_digit_state_code, st_premod_replacements, address_directi…
     |                                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1064 | …     lazy_chunk = clean_st_predir_lazy(lazy_chunk)
1065 | …     lazy_chunk = clean_st_pretyp_lazy(lazy_chunk, st_pretyp_replacements)
     |

F405 `st_premod_replacements` may be undefined, or defined from star imports
    --> projects/address-parser/src/pre_processing_nad_elements.py:1063:96
     |
1061 | …     lazy_chunk = clean_addnum_pre_lazy(lazy_chunk, complete_word_replacement_dict)
1062 | …     lazy_chunk = clean_addnum_suf_lazy(lazy_chunk)
1063 | …     lazy_chunk = clean_st_premod_lazy(lazy_chunk, full_state_name_to_two_digit_state_code, st_premod_replacements, address_directi…
     |                                                                                              ^^^^^^^^^^^^^^^^^^^^^^
1064 | …     lazy_chunk = clean_st_predir_lazy(lazy_chunk)
1065 | …     lazy_chunk = clean_st_pretyp_lazy(lazy_chunk, st_pretyp_replacements)
     |

F405 `address_directionals` may be undefined, or defined from star imports
    --> projects/address-parser/src/pre_processing_nad_elements.py:1063:120
     |
1061 | …word_replacement_dict)
1062 | …
1063 | …_name_to_two_digit_state_code, st_premod_replacements, address_directionals)
     |                                                         ^^^^^^^^^^^^^^^^^^^^
1064 | …
1065 | …replacements)
     |

F405 `st_pretyp_replacements` may be undefined, or defined from star imports
    --> projects/address-parser/src/pre_processing_nad_elements.py:1065:55
     |
1063 | …     lazy_chunk = clean_st_premod_lazy(lazy_chunk, full_state_name_to_two_digit_state_code, st_premod_replacements, address_directi…
1064 | …     lazy_chunk = clean_st_predir_lazy(lazy_chunk)
1065 | …     lazy_chunk = clean_st_pretyp_lazy(lazy_chunk, st_pretyp_replacements)
     |                                                     ^^^^^^^^^^^^^^^^^^^^^^
1066 | …     lazy_chunk = clean_st_name_lazy(lazy_chunk, complete_word_replacement_dict, usps_st_posttyp, address_directionals, list_of_add…
1067 | …     lazy_chunk = clean_st_posdir_lazy(lazy_chunk)
     |

F405 `complete_word_replacement_dict` may be undefined, or defined from star imports
    --> projects/address-parser/src/pre_processing_nad_elements.py:1066:53
     |
1064 | …     lazy_chunk = clean_st_predir_lazy(lazy_chunk)
1065 | …     lazy_chunk = clean_st_pretyp_lazy(lazy_chunk, st_pretyp_replacements)
1066 | …     lazy_chunk = clean_st_name_lazy(lazy_chunk, complete_word_replacement_dict, usps_st_posttyp, address_directionals, list_of_add…
     |                                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1067 | …     lazy_chunk = clean_st_posdir_lazy(lazy_chunk)
1068 | …     lazy_chunk = clean_st_posmod_lazy(lazy_chunk)
     |

F405 `usps_st_posttyp` may be undefined, or defined from star imports
    --> projects/address-parser/src/pre_processing_nad_elements.py:1066:85
     |
1064 | …     lazy_chunk = clean_st_predir_lazy(lazy_chunk)
1065 | …     lazy_chunk = clean_st_pretyp_lazy(lazy_chunk, st_pretyp_replacements)
1066 | …     lazy_chunk = clean_st_name_lazy(lazy_chunk, complete_word_replacement_dict, usps_st_posttyp, address_directionals, list_of_add…
     |                                                                                   ^^^^^^^^^^^^^^^
1067 | …     lazy_chunk = clean_st_posdir_lazy(lazy_chunk)
1068 | …     lazy_chunk = clean_st_posmod_lazy(lazy_chunk)
     |

F405 `address_directionals` may be undefined, or defined from star imports
    --> projects/address-parser/src/pre_processing_nad_elements.py:1066:102
     |
1064 | …     lazy_chunk = clean_st_predir_lazy(lazy_chunk)
1065 | …     lazy_chunk = clean_st_pretyp_lazy(lazy_chunk, st_pretyp_replacements)
1066 | …     lazy_chunk = clean_st_name_lazy(lazy_chunk, complete_word_replacement_dict, usps_st_posttyp, address_directionals, list_of_add…
     |                                                                                                    ^^^^^^^^^^^^^^^^^^^^
1067 | …     lazy_chunk = clean_st_posdir_lazy(lazy_chunk)
1068 | …     lazy_chunk = clean_st_posmod_lazy(lazy_chunk)
     |

F405 `list_of_address_directionals` may be undefined, or defined from star imports
    --> projects/address-parser/src/pre_processing_nad_elements.py:1066:124
     |
1064 | …
1065 | …ents)
1066 | …ement_dict, usps_st_posttyp, address_directionals, list_of_address_directionals)
     |                                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1067 | …
1068 | …
     |

Found 21 errors.
