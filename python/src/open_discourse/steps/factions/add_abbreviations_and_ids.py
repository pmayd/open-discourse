"""
Script to enhance the faction dataset with abbreviations and unique IDs.

This script is part of the Open Discourse pipeline and performs the following tasks:
1. Loads the basic factions data created by create.py
2. Adds standardized abbreviations to each faction using predefined mappings
3. Assigns unique numerical IDs to each faction based on their abbreviations
4. Saves the fully processed factions data to the final data directory

The resulting dataset is used throughout the Open Discourse project to standardize
faction references and provide consistent identifiers for parliamentary groups.
"""

import numpy as np
import pandas as pd

# Project-specific imports
from open_discourse.definitions import path
from open_discourse.helper.constants import FACTION_ABBREVIATIONS
from open_discourse.helper.io_utils import load_pickle, save_pickle
from open_discourse.helper.logging_config import setup_and_get_logger

# Configure a logger for this script
logger = setup_and_get_logger("process_factions")


def add_abbreviations_to_factions(factions_df: pd.DataFrame) -> None:
    """
    Adds abbreviations to faction names based on predefined mapping.
    Modifies the input DataFrame in-place.

    Args:
        factions_df (pd.DataFrame): DataFrame containing faction names in the 'faction_name' column.
                                   Will be modified in-place to include 'abbreviation' column.

    Raises:
        KeyError: If 'faction_name' column is missing from the input DataFrame
    """
    logger.info("Adding abbreviations to factions")

    # Insert new column at the beginning
    factions_df.insert(0, "abbreviation", "")

    # Track missing factions to log once at the end
    missing_factions = set()

    # Helper function to get abbreviation and track missing ones
    def get_and_track_abbreviation(faction_name):
        abbreviation = FACTION_ABBREVIATIONS.get(faction_name)
        if abbreviation is None:
            missing_factions.add(faction_name)
            return faction_name
        return abbreviation

    # Apply the function to each faction name
    factions_df["abbreviation"] = factions_df["faction_name"].apply(
        get_and_track_abbreviation
    )

    # Log any missing factions as warnings
    if missing_factions:
        logger.warning(
            f"Found {len(missing_factions)} faction names without abbreviation mappings: {missing_factions}"
        )
        logger.warning("Using original names as abbreviations for these factions")


def assign_ids_to_factions(factions_df: pd.DataFrame) -> None:
    """
    Assigns unique IDs to factions based on their abbreviations.
    Modifies the input DataFrame in-place.

    Args:
        factions_df (pd.DataFrame): DataFrame containing faction abbreviations in the 'abbreviation' column.
                                   Will be modified in-place to include 'id' column.

    Raises:
        KeyError: If 'abbreviation' column is missing from the input DataFrame
    """
    logger.info("Assigning IDs to factions based on abbreviations")

    # Get unique abbreviations and generate sequential IDs
    unique_abbreviations = np.unique(factions_df["abbreviation"])

    # Insert new ID column at the beginning with default value -1
    factions_df.insert(0, "id", -1)

    # Assign IDs based on abbreviations using enumerate
    for id_value, abbrev in enumerate(unique_abbreviations):
        factions_df.loc[factions_df["abbreviation"] == abbrev, "id"] = id_value

    logger.info(f"Assigned {len(unique_abbreviations)} unique IDs to factions")


def main(task):
    """
    Main function that loads factions data, adds abbreviations and IDs,
    and saves the result to the final directory.

    Returns:
        bool: True if the task was successful, False otherwise
    """
    # Define input/output paths
    FACTIONS_STAGE_01 = path.FACTIONS_STAGE_01
    DATA_FINAL = path.DATA_FINAL
    DATA_FINAL.mkdir(parents=True, exist_ok=True)

    # Load the factions data
    input_file = FACTIONS_STAGE_01 / "factions.pkl"
    factions = load_pickle(input_file, logger)
    if factions is None:
        return False  # Early return if loading failed
    # Process the data: add abbreviations and IDs
    try:
        # Add abbreviations
        add_abbreviations_to_factions(factions)

        # Add IDs based on abbreviations
        assign_ids_to_factions(factions)

        logger.info("Successfully processed factions data")
    except Exception as e:
        logger.error(f"Error processing factions data: {e}")
        return False
    # Save the processed data
    output_file = DATA_FINAL / "factions.pkl"
    if not save_pickle(factions, output_file, logger):
        return False  # Early return if saving failed

    logger.info("Script completed: factions abbreviations and IDs added.")
    return True


if __name__ == "__main__":
    main(None)
