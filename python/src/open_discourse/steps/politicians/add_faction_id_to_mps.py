"""
Script to add faction IDs to politicians (MPs) data by matching faction names.

This script is part of the Open Discourse data processing pipeline and performs the following tasks:
1. Loads factions data with predefined IDs
2. Loads politicians (MPs) data
3. Adds a faction_id column to the politicians data
4. Matches faction IDs based on matching the institution_name with faction_name
5. Saves the enhanced politicians data for further processing
"""

from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

# Project-specific imports
from open_discourse.definitions import path
from open_discourse.helper.io_utils import load_pickle, save_pickle
from open_discourse.helper.logging_config import setup_and_get_logger

# Configure a logger for this script
logger = setup_and_get_logger("process_politicians")


def load_required_data(
    politicians_path: Path, factions_path: Path
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Load the required politicians and factions DataFrames.

    Args:
        politicians_path (Path): Path to the politicians data file
        factions_path (Path): Path to the factions data file

    Returns:
        Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
            A tuple containing (politicians_df, factions_df) or (None, None) if loading failed
    """
    # Load factions data
    factions_df = load_pickle(factions_path / "factions.pkl", logger)
    if factions_df is None:
        return None, None

    # Verify factions DataFrame has required columns
    required_faction_cols = {"faction_name", "id"}
    if not required_faction_cols.issubset(factions_df.columns):
        missing = required_faction_cols - set(factions_df.columns)
        logger.error(f"Factions data is missing required columns: {missing}")
        return None, None

    # Load politicians data
    politicians_df = load_pickle(politicians_path / "mps.pkl", logger)
    if politicians_df is None:
        return None, None

    # Verify politicians DataFrame has required columns
    if "institution_name" not in politicians_df.columns:
        logger.error("Politicians data is missing required column: institution_name")
        return None, None

    logger.info(
        f"Loaded {len(politicians_df)} politician records and {len(factions_df)} faction records"
    )
    return politicians_df, factions_df


def add_faction_ids(
    politicians_df: pd.DataFrame, factions_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Add faction IDs to politicians data by matching institution_name with faction_name.

    This function matches politicians to factions by comparing the politician's institution_name
    field with the faction's faction_name field. When a match is found, the faction's ID is
    assigned to the politician's faction_id field.

    Args:
        politicians_df (pd.DataFrame): DataFrame containing politicians data with institution_name column
        factions_df (pd.DataFrame): DataFrame containing factions data with faction_name and id columns

    Returns:
        pd.DataFrame: Politicians DataFrame with added faction_id column
    """
    # Create a working copy to avoid modifying the input
    result_df = politicians_df.copy()

    # Add faction_id column with default value -1 (unmatched)
    if "faction_id" not in result_df.columns:
        result_df.insert(2, "faction_id", -1)
        logger.info("Added faction_id column to politicians data")

    # Track statistics
    match_count = 0
    total_factions = len(factions_df)

    # Match each faction to politicians
    for faction_name, faction_id in zip(factions_df["faction_name"], factions_df["id"]):
        # Find politicians with matching faction name and update their faction_id
        matches = result_df["institution_name"] == faction_name
        match_count_this_faction = matches.sum()

        if match_count_this_faction > 0:
            result_df.loc[matches, "faction_id"] = faction_id
            match_count += match_count_this_faction
            logger.debug(
                f"Matched {match_count_this_faction} politicians to faction '{faction_name}' (ID: {faction_id})"
            )

    # Log statistics
    unmatched_count = (result_df["faction_id"] == -1).sum()
    logger.info(f"Matched {match_count} politicians to {total_factions} factions")

    if unmatched_count > 0:
        logger.warning(
            f"{unmatched_count} politicians could not be matched to any faction"
        )

    return result_df


def main(task) -> bool:
    """
    Main function that orchestrates loading data, adding faction IDs,
    and saving the enhanced politicians data.

    Args:
        task: The doit task object (not used, but required for doit compatibility)

    Returns:
        bool: True for success, False for failure
    """
    # Define input/output paths
    POLITICIANS_INPUT = path.POLITICIANS_STAGE_01
    FACTIONS_INPUT = path.DATA_FINAL
    POLITICIANS_OUTPUT = path.POLITICIANS_STAGE_02

    # Create output directory if it doesn't exist
    POLITICIANS_OUTPUT.mkdir(parents=True, exist_ok=True)

    # Load required data
    politicians_df, factions_df = load_required_data(POLITICIANS_INPUT, FACTIONS_INPUT)
    if politicians_df is None or factions_df is None:
        logger.error("Failed to load required data, exiting")
        return False

    # Add faction IDs to politicians data
    try:
        enhanced_politicians = add_faction_ids(politicians_df, factions_df)
        logger.info("Successfully added faction IDs to politicians data")
    except Exception as e:
        logger.error(f"Error adding faction IDs to politicians data: {e}")
        return False

    # Save enhanced politicians data
    output_file = POLITICIANS_OUTPUT / "mps.pkl"
    if not save_pickle(enhanced_politicians, output_file, logger):
        return False

    logger.info("Script completed: add_faction_id_to_mps done.")
    return True


if __name__ == "__main__":
    main(None)
