# test_main.py
import pytest
from main import clean_string, clean_standardize_zip, clean_state, move_directionals, move_street_type, \
                move_unit_numbers

def test_clean_string_happy_path():
    assert clean_string(" \tHello  World\n! ") == "HELLO WORLD!"

def test_clean_string_null_handling():
    with pytest.raises(ValueError):
        clean_string(None)

def test_clean_string_empty():
    assert clean_string("") == ""

def test_clean_string_invalid_chars():
    assert clean_string("This\x00is\xa1\xa9\xa0valid.\x85") == "THISISALID."

def test_clean_standardize_zip_happy_path():
    assert clean_standardize_zip("12345") == "12345"
    assert clean_standardize_zip("1234") == "01234"
    assert clean_standardize_zip("12345-6789") == "12345"

def test_clean_standardize_zip_invalid():
    with pytest.raises(ValueError):
        clean_standardize_zip(None)
    with pytest.raises(ValueError):
        clean_standardize_zip("")
    with pytest.raises(ValueError):
        clean_standardize_zip("-12345")
    with pytest.raises(ValueError):
        clean_standardize_zip("1234.67")

def test_clean_state_happy_path():
    assert clean_state("Calif", ["CA"]) == "CA"

def test_clean_state_null_handling():
    assert clean_state(None, ["CA"]) == None

def test_clean_state_empty():
    assert clean_state("", ["CA"]) == None

def test_move_directionals_happy_path():
    st_name, st_predir, st_posdir = move_directionials("NORTHWEST", "EAST")
    assert st_name == ""
    assert st_predir == "NORTHWEST"
    assert st_posdir == "EAST"

def test_move_directionals_no_directional():
    st_name, st_predir, st_posdir = move_directionals("BROADWAY", "")
    assert st_name == "BROADWAY"
    assert st_predir == ""
    assert st_posdir == ""

def test_move_street_type_happy_path():
    st_name, st_postyp = move_street_type("MAIN STREET", ["ST"])
    assert st_name == "MAIN"
    assert st_postyp == "ST"

def test_move_street_type_no_match():
    st_name, st_postyp = move_street_type("BIG AVE", [])
    assert st_name == "BIG AVE"
    assert st_postyp == ""

def test_move_unit_numbers_happy_path():
    st_name, secondary_address = move_unit_numbers("123 MAIN ST APT 4B")
    assert st_name == "123 MAIN ST"
    assert secondary_address == "APT 4B"

def test_move_unit_numbers_no_units():
    st_name, secondary_address = move_unit_numbers("123 MAIN ST")
    assert st_name == "123 MAIN ST"
    assert secondary_address == ""