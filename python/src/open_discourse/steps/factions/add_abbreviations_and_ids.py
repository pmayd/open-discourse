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


def add_abbreviations_to_factions(factions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds abbreviations to faction names based on predefined mapping.

    Args:
        factions_df (pd.DataFrame): DataFrame containing faction names in the 'faction_name' column

    Returns:
        pd.DataFrame: DataFrame with an additional 'abbreviation' column at index 0. The original
                      data is preserved, and for faction names without a standard abbreviation,
                      the original faction name is used as the abbreviation.

    Raises:
        KeyError: If 'faction_name' column is missing from the input DataFrame
    """
    logger.info("Adding abbreviations to factions")

    # Create a copy to avoid modifying the input DataFrame
    result_df = factions_df.copy()

    # Insert new column at the beginning
    result_df.insert(0, "abbreviation", "")

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
    result_df["abbreviation"] = result_df["faction_name"].apply(
        get_and_track_abbreviation
    )

    # Log any missing factions as warnings
    if missing_factions:
        logger.warning(
            f"Found {len(missing_factions)} faction names without abbreviation mappings: {missing_factions}"
        )
        logger.warning("Using original names as abbreviations for these factions")

    return result_df


def assign_ids_to_factions(factions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Assigns unique IDs to factions based on their abbreviations.

    Args:
        factions_df (pd.DataFrame): DataFrame containing faction abbreviations in the 'abbreviation' column

    Returns:
        pd.DataFrame: DataFrame with an additional 'id' column at index 0

    Raises:
        KeyError: If 'abbreviation' column is missing from the input DataFrame
    """
    logger.info("Assigning IDs to factions based on abbreviations")

    # Create a copy to avoid modifying the input DataFrame
    result_df = factions_df.copy()

    # Get unique abbreviations and generate sequential IDs
    unique_abbreviations = np.unique(result_df["abbreviation"])

    # Insert new ID column at the beginning with default value -1
    result_df.insert(0, "id", -1)

    # Assign IDs based on abbreviations using enumerate
    for id_value, abbrev in enumerate(unique_abbreviations):
        result_df.loc[result_df["abbreviation"] == abbrev, "id"] = id_value

    logger.info(f"Assigned {len(unique_abbreviations)} unique IDs to factions")
    return result_df


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
        factions_with_abbrevs = add_abbreviations_to_factions(factions)

        # Add IDs based on abbreviations
        final_factions = assign_ids_to_factions(factions_with_abbrevs)

        logger.info("Successfully processed factions data")
    except TypeError as e:
        logger.error(f"Type error during faction processing: {e}")
        return False
    except ValueError as e:
        logger.error(f"Value error during faction processing: {e}")
        return False
    except KeyError as e:
        logger.error(f"Key error during faction processing (missing column?): {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error processing factions data: {e}")
        return False
    # Save the processed data
    output_file = DATA_FINAL / "factions.pkl"
    if not save_pickle(final_factions, output_file, logger):
        return False  # Early return if saving failed

    logger.info("Script completed: factions abbreviations and IDs added.")
    return True


if __name__ == "__main__":
    main(None)
