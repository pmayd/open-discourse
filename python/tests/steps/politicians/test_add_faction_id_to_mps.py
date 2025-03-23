"""Tests for the add_faction_id_to_mps module."""

import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from open_discourse.steps.politicians.add_faction_id_to_mps import (
    load_required_data,
    add_faction_ids,
    main,
)


class TestAddFactionIdToMPs:
    """Tests for the add_faction_id_to_mps module functions."""

    @pytest.fixture
    def mock_politicians_df(self):
        """Create a mock politicians DataFrame for testing."""
        return pd.DataFrame({
            "ui": ["1", "2", "3", "4"],
            "electoral_term": [19, 19, 19, 19],
            "first_name": ["John", "Jane", "Bob", "Alice"],
            "last_name": ["Doe", "Smith", "Brown", "Johnson"],
            "institution_name": ["SPD", "CDU/CSU", "FDP", "Unknown"],
        })

    @pytest.fixture
    def mock_factions_df(self):
        """Create a mock factions DataFrame for testing."""
        return pd.DataFrame({
            "id": [1, 2, 3],
            "abbreviation": ["SPD", "CDU/CSU", "FDP"],
            "faction_name": ["SPD", "CDU/CSU", "FDP"],
        })

    @patch('open_discourse.steps.politicians.add_faction_id_to_mps.load_pickle')
    def test_load_required_data_success(self, mock_load_pickle, mock_politicians_df, mock_factions_df):
        """Test successful loading of required data."""
        # Setup mocks to return our test DataFrames
        mock_load_pickle.side_effect = [mock_factions_df, mock_politicians_df]
        
        # Call the function
        politicians_df, factions_df = load_required_data(Path("/test/politicians"), Path("/test/factions"))
        
        # Check that the function returned our test DataFrames
        assert politicians_df is not None
        assert factions_df is not None
        assert politicians_df.equals(mock_politicians_df)
        assert factions_df.equals(mock_factions_df)

    @patch('open_discourse.steps.politicians.add_faction_id_to_mps.load_pickle')
    def test_load_required_data_factions_missing_columns(self, mock_load_pickle, mock_politicians_df):
        """Test handling when factions DataFrame is missing required columns."""
        # Create a factions DataFrame missing required columns
        bad_factions_df = pd.DataFrame({"id": [1, 2, 3]})  # Missing faction_name
        
        # Setup mocks
        mock_load_pickle.side_effect = [bad_factions_df, mock_politicians_df]
        
        # Call the function
        result = load_required_data(Path("/test/politicians"), Path("/test/factions"))
        
        # Check that the function returned None for both DataFrames
        assert result == (None, None)

    @patch('open_discourse.steps.politicians.add_faction_id_to_mps.load_pickle')
    def test_load_required_data_politicians_missing_columns(self, mock_load_pickle, mock_factions_df):
        """Test handling when politicians DataFrame is missing required columns."""
        # Create a politicians DataFrame missing required columns
        bad_politicians_df = pd.DataFrame({
            "ui": ["1", "2", "3"],
            "electoral_term": [19, 19, 19],
            # Missing institution_name
        })
        
        # Setup mocks
        mock_load_pickle.side_effect = [mock_factions_df, bad_politicians_df]
        
        # Call the function
        result = load_required_data(Path("/test/politicians"), Path("/test/factions"))
        
        # Check that the function returned None for both DataFrames
        assert result == (None, None)

    def test_add_faction_ids(self, mock_politicians_df, mock_factions_df):
        """Test adding faction IDs to politicians."""
        # Call the function
        result_df = add_faction_ids(mock_politicians_df, mock_factions_df)
        
        # Check that the function added the faction_id column
        assert "faction_id" in result_df.columns
        
        # Check that the faction IDs were assigned correctly
        assert result_df.loc[result_df["institution_name"] == "SPD", "faction_id"].iloc[0] == 1
        assert result_df.loc[result_df["institution_name"] == "CDU/CSU", "faction_id"].iloc[0] == 2
        assert result_df.loc[result_df["institution_name"] == "FDP", "faction_id"].iloc[0] == 3
        assert result_df.loc[result_df["institution_name"] == "Unknown", "faction_id"].iloc[0] == -1

    def test_add_faction_ids_with_existing_column(self, mock_politicians_df, mock_factions_df):
        """Test adding faction IDs when the faction_id column already exists."""
        # Add the faction_id column with some initial values
        mock_politicians_df["faction_id"] = -99
        
        # Call the function
        result_df = add_faction_ids(mock_politicians_df, mock_factions_df)
        
        # Check that the function updated the faction_id column
        assert result_df.loc[result_df["institution_name"] == "SPD", "faction_id"].iloc[0] == 1
        assert result_df.loc[result_df["institution_name"] == "CDU/CSU", "faction_id"].iloc[0] == 2
        assert result_df.loc[result_df["institution_name"] == "FDP", "faction_id"].iloc[0] == 3
        assert result_df.loc[result_df["institution_name"] == "Unknown", "faction_id"].iloc[0] == -99

    @patch('open_discourse.steps.politicians.add_faction_id_to_mps.load_required_data')
    @patch('open_discourse.steps.politicians.add_faction_id_to_mps.add_faction_ids')
    @patch('open_discourse.steps.politicians.add_faction_id_to_mps.save_pickle')
    def test_main_success(self, mock_save_pickle, mock_add_faction_ids, mock_load_required_data, 
                         mock_politicians_df, mock_factions_df):
        """Test successful execution of the main function."""
        # Setup mocks
        mock_load_required_data.return_value = (mock_politicians_df, mock_factions_df)
        mock_add_faction_ids.return_value = mock_politicians_df
        mock_save_pickle.return_value = True
        
        # Call the main function
        result = main(None)
        
        # Verify the result and that all expected functions were called
        assert result is True
        mock_load_required_data.assert_called_once()
        mock_add_faction_ids.assert_called_once_with(mock_politicians_df, mock_factions_df)
        mock_save_pickle.assert_called_once()

    @patch('open_discourse.steps.politicians.add_faction_id_to_mps.load_required_data')
    def test_main_load_data_failure(self, mock_load_required_data):
        """Test main function handling when load_required_data fails."""
        # Setup mock to return None (failure)
        mock_load_required_data.return_value = (None, None)
        
        # Call the main function
        result = main(None)
        
        # Verify the result
        assert result is False
        mock_load_required_data.assert_called_once()

    @patch('open_discourse.steps.politicians.add_faction_id_to_mps.load_required_data')
    @patch('open_discourse.steps.politicians.add_faction_id_to_mps.add_faction_ids')
    def test_main_add_faction_ids_failure(self, mock_add_faction_ids, mock_load_required_data,
                                         mock_politicians_df, mock_factions_df):
        """Test main function handling when add_faction_ids fails."""
        # Setup mocks
        mock_load_required_data.return_value = (mock_politicians_df, mock_factions_df)
        mock_add_faction_ids.side_effect = Exception("Adding faction IDs failed")
        
        # Call the main function
        result = main(None)
        
        # Verify the result
        assert result is False
        mock_load_required_data.assert_called_once()
        mock_add_faction_ids.assert_called_once_with(mock_politicians_df, mock_factions_df)