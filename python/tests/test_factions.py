import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

# Import the functions from the correct package path
from open_discourse.helper.constants import ADDITIONAL_FACTIONS, FACTION_ABBREVIATIONS
from open_discourse.steps.factions.create import extract_unique_factions, main as create_main
from open_discourse.steps.factions.add_abbreviations_and_ids import (
    add_abbreviations_to_factions,
    assign_ids_to_factions,
    main as add_abbrevs_main
)


def test_extract_unique_factions():
    # Create a test DataFrame with mock MP data
    test_data = {
        "institution_type": [
            "Fraktion/Gruppe",
            "Fraktion/Gruppe",
            "Other",
            "Fraktion/Gruppe",
        ],
        "institution_name": ["Fraktion A", "Fraktion B", "Other Org", "Fraktion A"],
    }
    mps_df = pd.DataFrame(test_data)

    # Run the actual function
    result = extract_unique_factions(mps_df)

    # Verify the result contains unique factions plus additional factions
    expected_factions = list({"Fraktion A", "Fraktion B"})
    expected_factions.extend(ADDITIONAL_FACTIONS)
    expected_df = pd.DataFrame(expected_factions, columns=["faction_name"])

    # Ensure the result has the correct columns and unique values
    assert "faction_name" in result.columns
    assert len(result) == len(expected_factions)
    assert set(result["faction_name"]) == set(expected_df["faction_name"])


def test_extract_unique_factions_missing_columns():
    # Test with a DataFrame missing required columns
    test_data = {
        "wrong_column": ["Fraktion A", "Fraktion B"],
    }
    mps_df = pd.DataFrame(test_data)

    # Verify that the correct error is raised
    with pytest.raises(ValueError, match="Missing required columns"):
        extract_unique_factions(mps_df)


def test_add_abbreviations_to_factions():
    # Create a test DataFrame with faction names
    test_data = {
        "faction_name": [
            "Fraktion der CDU/CSU (Gast)",
            "Fraktion der SPD (Gast)",
            "Unknown Faction",  # This should not be in the abbreviations dict
        ]
    }
    factions_df = pd.DataFrame(test_data)

    # Run the actual function (modifies in-place)
    add_abbreviations_to_factions(factions_df)

    # Verify the abbreviations were added correctly
    assert "abbreviation" in factions_df.columns
    assert factions_df.loc[0, "abbreviation"] == "CDU/CSU"
    assert factions_df.loc[1, "abbreviation"] == "SPD"
    assert (
        factions_df.loc[2, "abbreviation"] == "Unknown Faction"
    )  # Should fall back to original name


@pytest.mark.parametrize(
    "input_data, expected_abbrevs",
    [
        (
            ["Fraktion der CDU/CSU (Gast)", "Fraktion der SPD (Gast)"],
            ["CDU/CSU", "SPD"],
        ),
        (
            ["Fraktion Bündnis 90/Die Grünen", "Fraktion Die Grünen"],
            ["Bündnis 90/Die Grünen", "Bündnis 90/Die Grünen"],
        ),
        (
            ["Unknown Faction 1", "Unknown Faction 2"],
            ["Unknown Faction 1", "Unknown Faction 2"],
        ),
    ],
)
def test_add_abbreviations_parametrized(input_data, expected_abbrevs):
    # Create a test DataFrame with different faction names
    test_df = pd.DataFrame({"faction_name": input_data})

    # Run the actual function (modifies in-place)
    add_abbreviations_to_factions(test_df)

    # Verify the results match expected abbreviations
    assert list(test_df["abbreviation"]) == expected_abbrevs


def test_assign_ids_to_factions():
    # Create a test DataFrame with faction abbreviations
    test_data = {
        "faction_name": ["Faction A", "Faction B", "Faction C", "Faction A"],
        "abbreviation": ["A", "B", "C", "A"],
    }
    factions_df = pd.DataFrame(test_data)

    # Run the actual function (modifies in-place)
    assign_ids_to_factions(factions_df)

    # Verify the IDs were assigned correctly
    assert "id" in factions_df.columns

    # Test that same abbreviations get same IDs
    assert factions_df.loc[0, "id"] == factions_df.loc[3, "id"]

    # Test that different abbreviations get different IDs
    assert len(set(factions_df["id"])) == 3

    # Test that IDs are sequential starting from 0
    assert set(factions_df["id"]) == {0, 1, 2}


def test_full_pipeline():
    """Test the entire faction processing pipeline."""
    # Create input data for the first step
    mps_data = {
        "institution_type": ["Fraktion/Gruppe", "Fraktion/Gruppe", "Other"],
        "institution_name": [
            "Fraktion der CDU/CSU (Gast)",
            "Fraktion der SPD (Gast)",
            "Other Org",
        ],
    }
    mps_df = pd.DataFrame(mps_data)

    # Step 1: Extract unique factions
    factions_df = extract_unique_factions(mps_df)

    # Step 2: Add abbreviations (modifies in-place)
    add_abbreviations_to_factions(factions_df)

    # Step 3: Assign IDs (modifies in-place)
    assign_ids_to_factions(factions_df)

    # Verify the entire pipeline produces the expected result
    assert set(factions_df["faction_name"]).issuperset(
        {"Fraktion der CDU/CSU (Gast)", "Fraktion der SPD (Gast)"}
    )

    # Find the rows for our test factions
    cdu_row = factions_df[
        factions_df["faction_name"] == "Fraktion der CDU/CSU (Gast)"
    ]
    spd_row = factions_df[
        factions_df["faction_name"] == "Fraktion der SPD (Gast)"
    ]

    # Check abbreviations are correct
    assert cdu_row["abbreviation"].values[0] == "CDU/CSU"
    assert spd_row["abbreviation"].values[0] == "SPD"

    # Check IDs exist and are valid
    assert cdu_row["id"].values[0] >= 0
    assert spd_row["id"].values[0] >= 0


def test_create_main_function():
    """Test the main() function from create.py."""
    # Create test data
    test_mps = pd.DataFrame({
        "institution_type": ["Fraktion/Gruppe", "Fraktion/Gruppe"],
        "institution_name": ["Test Faction 1", "Test Faction 2"]
    })
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Mock the path module to use our temp directory
        with patch('open_discourse.steps.factions.create.path') as mock_path:
            # Setup mock paths
            mock_path.POLITICIANS_STAGE_01 = tmp_path / "politicians_stage_01"
            mock_path.FACTIONS_STAGE_01 = tmp_path / "factions_stage_01"
            
            # Create the input directory and file
            mock_path.POLITICIANS_STAGE_01.mkdir(parents=True, exist_ok=True)
            mps_file = mock_path.POLITICIANS_STAGE_01 / "mps.pkl"
            
            # Save test data
            test_mps.to_pickle(mps_file)
            
            # Run the main function
            result = create_main(None)
            
            # Check that it succeeded
            assert result is True
            
            # Check that output file was created
            output_file = mock_path.FACTIONS_STAGE_01 / "factions.pkl"
            assert output_file.exists()
            
            # Load and verify the output
            created_factions = pd.read_pickle(output_file)
            assert "faction_name" in created_factions.columns
            assert len(created_factions) >= 2  # At least our test factions
            
            # Verify test factions are present
            faction_names = set(created_factions["faction_name"])
            assert "Test Faction 1" in faction_names
            assert "Test Faction 2" in faction_names


def test_add_abbreviations_and_ids_main_function():
    """Test the main() function from add_abbreviations_and_ids.py."""
    # Create test factions data
    test_factions = pd.DataFrame({
        "faction_name": [
            "Fraktion der CDU/CSU (Gast)",
            "Fraktion der SPD (Gast)",
            "Unknown Faction"
        ]
    })
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Mock the path module
        with patch('open_discourse.steps.factions.add_abbreviations_and_ids.path') as mock_path:
            # Setup mock paths
            mock_path.FACTIONS_STAGE_01 = tmp_path / "factions_stage_01"
            mock_path.DATA_FINAL = tmp_path / "data_final"
            
            # Create input directory and file
            mock_path.FACTIONS_STAGE_01.mkdir(parents=True, exist_ok=True)
            input_file = mock_path.FACTIONS_STAGE_01 / "factions.pkl"
            
            # Save test data
            test_factions.to_pickle(input_file)
            
            # Run the main function
            result = add_abbrevs_main(None)
            
            # Check that it succeeded
            assert result is True
            
            # Check that output file was created
            output_file = mock_path.DATA_FINAL / "factions.pkl"
            assert output_file.exists()
            
            # Load and verify the output
            final_factions = pd.read_pickle(output_file)
            
            # Check all expected columns exist
            assert "id" in final_factions.columns
            assert "abbreviation" in final_factions.columns
            assert "faction_name" in final_factions.columns
            
            # Check column order (id, abbreviation, faction_name)
            assert list(final_factions.columns) == ["id", "abbreviation", "faction_name"]
            
            # Verify abbreviations were added correctly
            cdu_row = final_factions[final_factions["faction_name"] == "Fraktion der CDU/CSU (Gast)"]
            assert len(cdu_row) == 1
            assert cdu_row["abbreviation"].values[0] == "CDU/CSU"
            
            # Verify IDs were assigned
            assert final_factions["id"].min() >= 0
            assert len(final_factions["id"].unique()) == len(final_factions["abbreviation"].unique())
