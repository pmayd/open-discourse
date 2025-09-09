"""
Script to extract and create a basic factions dataset from politicians' data.

This script is part of the Open Discourse pipeline and performs the following tasks:
1. Loads politicians' data from a pickle file
2. Extracts unique faction names where institution_type is "Fraktion/Gruppe"
3. Adds additional predefined factions from constants
4. Saves the resulting factions DataFrame to a pickle file

The output of this script serves as input for the subsequent faction processing step
which adds abbreviations and unique IDs.
"""

import numpy as np
import pandas as pd

# Project-specific imports
from open_discourse.definitions import path
from open_discourse.helper.constants import ADDITIONAL_FACTIONS
from open_discourse.helper.io_utils import load_pickle, save_pickle
from open_discourse.helper.logging_config import setup_and_get_logger

# Configure a logger for this script
logger = setup_and_get_logger("process_factions")


def extract_unique_factions(mps: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts unique faction names from the given politicians DataFrame and appends additional predefined factions.

    This function filters the input DataFrame to include only rows where 'institution_type' is "Fraktion/Gruppe",
    then extracts unique faction names from the 'institution_name' column. It also appends any additional factions
    specified in the ADDITIONAL_FACTIONS constant.

    Args:
        mps (pd.DataFrame): A DataFrame containing politicians' data. It must include the columns
            'institution_type' and 'institution_name'.

    Returns:
        pd.DataFrame: A DataFrame with a single column "faction_name" that contains the unique faction names
            extracted from the input DataFrame, including the additional factions. The DataFrame will have
            the shape (n, 1) where n is the number of unique factions plus additional predefined factions.

    Raises:
        ValueError: If the input DataFrame is missing required columns ('institution_type' or 'institution_name').
    """
    # Cut dataframe down to two columns
    required_cols = {"institution_type", "institution_name"}
    if not required_cols.issubset(mps.columns):
        missing = required_cols - set(mps.columns)
        logger.error(f"Missing required columns in DataFrame: {missing}")
        raise ValueError(f"Missing required columns in DataFrame: {missing}")

    # Filter rows where institution_type is "Fraktion/Gruppe"
    factions = mps.loc[
        mps["institution_type"] == "Fraktion/Gruppe", "institution_name"
    ]

    # Extract unique faction names
    unique_factions = np.unique(factions)

    # Append additional predefined factions
    all_factions = np.append(unique_factions, ADDITIONAL_FACTIONS)

    # Convert the result to a DataFrame, will eventually be saved to file
    return pd.DataFrame(all_factions, columns=["faction_name"])


def main(task):
    """
    Main function that loads the mps DataFrame, extracts unique factions,
    and saves them to 'factions.pkl' in the designated output directory.

    This function orchestrates the following steps:
    1. Loads politicians data from the POLITICIANS_STAGE_01 directory
    2. Extracts unique faction names using extract_unique_factions()
    3. Saves the resulting DataFrame to the FACTIONS_STAGE_01 directory

    Returns:
        bool: True if the task was successful, False otherwise
    """
    # Define input/output paths
    POLITICIANS_STAGE_01 = path.POLITICIANS_STAGE_01
    FACTIONS_STAGE_01 = path.FACTIONS_STAGE_01
    FACTIONS_STAGE_01.mkdir(parents=True, exist_ok=True)

    # Load the politicians' data from a pickle file for further processing
    mps_path = POLITICIANS_STAGE_01 / "mps.pkl"
    mps = load_pickle(mps_path, logger)
    if mps is None:
        logger.error(f"Failed to load politicians data from {mps_path}")
        return False  # Early return if loading failed

    # Extract the unique names of factions/groups from the politicians' data via extract_unique_factions()
    try:
        unique_factions_df = extract_unique_factions(mps)
        logger.info("Extracted unique factions successfully.")
    except ValueError as ve:
        logger.error(f"Data validation error: {ve}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during faction extraction: {e}")
        return False

    # Save the unique factions DataFrame, final log after success
    output_file = FACTIONS_STAGE_01 / "factions.pkl"
    if not save_pickle(unique_factions_df, output_file, logger):
        return False  # Early return if saving failed

    logger.info("Script completed: factions creation done.")
    return True


if __name__ == "__main__":
    main(None)
