import tempfile
from pathlib import Path

import pandas as pd
import pyparsing as pp
import pytest

from open_discourse.helper.io_utils import load_pickle, save_pickle
from open_discourse.helper.logging_config import setup_and_get_logger
from open_discourse.helper.utils import get_term_from_path

term_number_parser = pp.Literal("electoral_term") + "_" + pp.Word(pp.nums, exact=2)


@pytest.mark.parametrize(
    "folder_path, expected",
    [
        (Path("/some/path/electoral_term_pp12"), 12),
        (Path("/some/path/no_term"), None),
        (Path("/some/path/electoral_term_abc"), None),
        (Path("/12_electoral_term/path"), None),
        (Path("/path/electoral_term_pp03"), 3),
        (Path("/path/electoral_term_pp56/another_term_pp78"), 56),
        (Path("/path/electoral_term_pp04"), 4),
    ],
)
def test_get_term_from_path(folder_path, expected):
    assert get_term_from_path(folder_path) == expected


# Tests for I/O utilities
def test_pickle_roundtrip():
    """Test that data survives being saved and loaded via pickle."""
    logger = setup_and_get_logger("test_io")
    
    # Create test data
    test_df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "value": [10.5, 20.3, 30.1]
    })
    
    # Use a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
        
        try:
            # Save the DataFrame
            success = save_pickle(test_df, tmp_path, logger)
            assert success is True, "save_pickle should return True on success"
            assert tmp_path.exists(), "File should exist after saving"
            
            # Load it back
            loaded_df = load_pickle(tmp_path, logger)
            
            # Verify the data is identical
            assert loaded_df is not None, "Loaded data should not be None"
            pd.testing.assert_frame_equal(test_df, loaded_df)
            
        finally:
            # Clean up
            if tmp_path.exists():
                tmp_path.unlink()


def test_pickle_with_complex_dataframe():
    """Test pickle I/O with a more complex DataFrame including various data types."""
    logger = setup_and_get_logger("test_io")
    
    # Create a complex DataFrame similar to what the factions pipeline uses
    test_df = pd.DataFrame({
        "id": [0, 1, 2, 0],  # Duplicate IDs like in faction data
        "faction_name": ["Fraktion A", "Fraktion B", "Fraktion C", "Fraktion A"],
        "abbreviation": ["A", "B", "C", "A"],
        "nested_list": [[1, 2], [3, 4], [5, 6], [1, 2]],
        "mixed_types": [1, "string", 3.14, None]
    })
    
    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
        
        try:
            # Save and load
            assert save_pickle(test_df, tmp_path, logger) is True
            loaded_df = load_pickle(tmp_path, logger)
            
            # Verify
            assert loaded_df is not None
            pd.testing.assert_frame_equal(test_df, loaded_df)
            
            # Check that data types are preserved
            assert loaded_df["id"].dtype == test_df["id"].dtype
            assert loaded_df["faction_name"].dtype == test_df["faction_name"].dtype
            
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


def test_pickle_preserves_column_order():
    """Test that column order is preserved through pickle I/O."""
    logger = setup_and_get_logger("test_io")
    
    # Create DataFrame with specific column order (like factions data)
    test_df = pd.DataFrame({
        "faction_name": ["A", "B"],
    })
    test_df.insert(0, "abbreviation", ["abbr_A", "abbr_B"])
    test_df.insert(0, "id", [0, 1])
    
    # Verify initial column order
    assert list(test_df.columns) == ["id", "abbreviation", "faction_name"]
    
    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
        
        try:
            save_pickle(test_df, tmp_path, logger)
            loaded_df = load_pickle(tmp_path, logger)
            
            # Verify column order is preserved
            assert list(loaded_df.columns) == ["id", "abbreviation", "faction_name"]
            pd.testing.assert_frame_equal(test_df, loaded_df)
            
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
