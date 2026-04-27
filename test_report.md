### Summary

**Failed** - lint issues: **21**, tests: **1 failed, 0 collected**

### Checks

| Check | Result    | Detail                      |
|-------|-----------|----------------------------|
| Lint (ruff)     | FAIL / 21 issues  | Multiple linting errors found, primarily about duplicate dictionary keys and incorrect imports. |
| Tests (pytest)   | FAIL / 1 failure | Import error while collecting tests in `test_main.py`. |

### Lint Issues

- **projects/address-parser/src/address_reference.py:69**: F601 Dictionary key literal `"MOORESVILLE"` repeated
- **projects/address-parser/src/address_reference.py:72**: F601 Dictionary key literal `"NE"` repeated
- **projects/address-parser/src/pre_processing_nad_elements.py:28**: E402 Module level import not at top of file, F403 `from address.address_functions import *` used
- **projects/address-parser/src/pre_processing_nad_elements.py:29**: E402 Module level import not at top of file, F403 `from address.address_reference import *` used
- **projects/address-parser/src/pre_processing_nad_elements.py:30**: E402 Module level import not at top of file, F403 `from address.united_states_zipcodes_functions import *` used
- **projects/address-parser/src/pre_processing_nad_elements.py:31**: E402 Module level import not at top of file, F403 `from address.national_address_database_functions import *` used
- **projects/address-parser/src/pre_processing_nad_elements.py:668**: F405 `clean_string` may be undefined or defined from star imports
- **projects/address-parser/src/pre_processing_nad_elements.py:673**: F405 `city_name_standardize_whole_words` may be undefined or defined from star imports
- **projects/address-parser/src/pre_processing_nad_elements.py:1061**: F405 `complete_word_replacement_dict` may be undefined, or defined from star imports
- **projects/address-parser/src/pre_processing_nad_elements.py:1063**: Multiple instances of F405 for variables like `full_state_name_to_two_digit_state_code`, `st_premod_replacements`, `address_directionals`, `st_pretyp_replacements`, `usps_st_posttyp`, and `list_of_address_directionals` may be undefined or defined from star imports

### Test Failures

- **projects/address-parser/tests/test_main.py**: ImportError while importing test module due to inability to import `clean_string` from `main`.

### Fix Priority

1. **Fix dictionary key repetition**:
   - Remove duplicate keys in `projects/address-parser/src/address_reference.py` at lines 69 and 72.

2. **Organize imports correctly**:
   - Move all top-level imports to the top of the file in `projects/address-parser/src/pre_processing_nad_elements.py`.
   - Replace wildcard imports with explicit named imports, e.g., 
     ```python
     from address.address_functions import specific_function_1, specific_function_2
     ```

3. **Resolve undefined names**:
   - Ensure all used functions such as `clean_string`, `city_name_standardize_whole_words`, `complete_word_replacement_dict`, etc., are correctly imported or defined within the relevant scope in `projects/address-parser/src/pre_processing_nad_elements.py`.

4. **Fix import error in tests**:
   - Correct the import statement or module structure so that `test_main.py` can successfully import from `main`. If necessary, create a __init__.py file in the src directory to include __all__ submodules or modules.

By addressing these issues in order, the lint errors will be resolved first, following by test failures.