"""
Script to merge politicians data from multiple sources (MPs and government members).

This script is part of the Open Discourse data processing pipeline and performs the following tasks:
1. Loads politicians (MPs) data with faction IDs
2. Loads government members (ministers) data
3. Matches government members to existing MPs where possible
4. Creates new politician entries for government members not found in MPs data
5. Standardizes faction names using regex pattern matching
6. Saves the merged politicians data for further processing
"""

import pandas as pd
import regex
from tqdm import tqdm
from typing import Dict, List, Union, Optional, Any, Tuple
from pathlib import Path

# Project-specific imports
from open_discourse.definitions import path
from open_discourse.helper.logging_config import setup_and_get_logger
from open_discourse.helper.io_utils import load_pickle, save_pickle
from open_discourse.helper.constants import ELECTORAL_TERMS, FACTION_PATTERNS

# Configure a logger for this script
logger = setup_and_get_logger("merge_politicians")

def load_politicians_data(
    mps_path: Path, mgs_path: Path, factions_path: Path
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Load the required politicians data from different sources.
    
    Args:
        mps_path (Path): Path to the MPs (parliamentarians) data
        mgs_path (Path): Path to the government members data
        factions_path (Path): Path to the factions data
        
    Returns:
        Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
            A tuple containing (mps_df, mgs_df, factions_df) or None values if loading failed
    """
    # Load MPs data
    mps_df = load_pickle(mps_path / "mps.pkl", logger)
    if mps_df is None:
        return None, None, None
    
    # Load government members data
    mgs_df = load_pickle(mgs_path / "mgs.pkl", logger)
    if mgs_df is None:
        return None, None, None
    
    # Load factions data
    factions_df = load_pickle(factions_path / "factions.pkl", logger)
    if factions_df is None:
        return None, None, None
    
    # Verify critical columns exist
    required_mps_cols = {"ui", "first_name", "last_name", "birth_date"}
    if not required_mps_cols.issubset(mps_df.columns):
        missing = required_mps_cols - set(mps_df.columns)
        logger.error(f"MPs data is missing required columns: {missing}")
        return None, None, None
    
    required_mgs_cols = {"first_name", "last_name", "birth_date", "position", "position_from", "position_until", "faction"}
    if not required_mgs_cols.issubset(mgs_df.columns):
        missing = required_mgs_cols - set(mgs_df.columns)
        logger.error(f"Government members data is missing required columns: {missing}")
        return None, None, None
    
    required_factions_cols = {"id", "abbreviation"}
    if not required_factions_cols.issubset(factions_df.columns):
        missing = required_factions_cols - set(factions_df.columns)
        logger.error(f"Factions data is missing required columns: {missing}")
        return None, None, None
    
    logger.info(f"Loaded {len(mps_df)} MPs, {len(mgs_df)} government members, and {len(factions_df)} factions")
    return mps_df, mgs_df, factions_df

def get_faction_abbrev(faction: str, faction_patterns: Dict[str, str]) -> Optional[str]:
    """
    Match a faction name to a standardized abbreviation using regex patterns.
    
    Args:
        faction (str): The faction name to match
        faction_patterns (Dict[str, str]): Dictionary mapping faction abbreviations to regex patterns
        
    Returns:
        Optional[str]: The matched faction abbreviation or None if no match found
    """
    for faction_abbrev, faction_pattern in faction_patterns.items():
        if regex.search(faction_pattern, faction):
            return faction_abbrev
    return None

def get_electoral_term(from_year: Optional[int] = None, to_year: Optional[int] = None) -> Union[int, List[int]]:
    """
    Determine electoral term(s) based on start and/or end years.
    
    Args:
        from_year (Optional[int]): Start year of a period
        to_year (Optional[int]): End year of a period
        
    Returns:
        Union[int, List[int]]: Single electoral term or list of electoral terms
        
    Raises:
        AttributeError: If neither from_year nor to_year is provided
        ValueError: If the years are outside the range of known electoral terms
    """
    # Unpack electoral terms data
    from_years = ELECTORAL_TERMS["from"]
    until_years = ELECTORAL_TERMS["until"]
    
    if not from_year and not to_year:
        raise AttributeError("At least one of from_year or to_year must be provided")
    
    # Case 1: Only to_year provided
    elif from_year is None:
        if to_year in until_years:
            return until_years.index(to_year) + 1
        else:
            # Handle special case for years after the last defined electoral term
            if to_year > 2017:
                return 19  # Latest electoral term
                
            # Find the first electoral term that ends after the given year
            for counter, year in enumerate(until_years):
                if year > to_year:
                    return counter + 1
                    
            raise ValueError(f"Year {to_year} is outside known electoral terms")
    
    # Case 2: Only from_year provided
    elif to_year is None:
        if from_year in from_years:
            return from_years.index(from_year) + 1
        else:
            # Handle special case for years after the last defined electoral term
            if from_year > 2017:
                return 19  # Latest electoral term
                
            # Find the first electoral term that starts after the given year
            for counter, year in enumerate(from_years):
                if year > from_year:
                    return counter
                    
            raise ValueError(f"Year {from_year} is outside known electoral terms")
    
    # Case 3: Both from_year and to_year provided
    else:
        from_term = get_electoral_term(from_year=from_year, to_year=None)
        to_term = get_electoral_term(from_year=None, to_year=to_year)
        
        if from_term != to_term:
            return list(range(from_term, to_term + 1))
        else:
            return [from_term]

def normalize_name(name: str) -> str:
    """
    Normalize a name by replacing hyphens with spaces.
    
    Args:
        name (str): Name to normalize
        
    Returns:
        str: Normalized name
    """
    return regex.sub("-", " ", name)

def _fix_special_case_names(last_name: str, first_names: List[str]) -> Tuple[List[str], Optional[str]]:
    """
    Handle special case name corrections and faction overrides.
    
    Args:
        last_name (str): Last name of politician
        first_names (List[str]): List containing first name(s) of politician
        
    Returns:
        Tuple[List[str], Optional[str]]: Tuple of (corrected_first_names, faction_override or None)
    """
    faction_override = None
    
    # Special case handling based on name patterns
    if last_name == "Fischer" and first_names[0] == "Joschka":
        first_names = ["Joseph"]
    elif last_name == "Waigel" and first_names[0] == "Theo":
        first_names = ["Theodor"]
    elif last_name == "Baum" and first_names[0] == "Gerhart":
        first_names = ["Gerhart Rudolf"]
    elif last_name == "Heinemann" and first_names[0] == "Gustav":
        first_names = ["Gustav W."]
    elif last_name == "Lehr" and first_names[0] == "Ursula":
        first_names = ["Ursula Maria"]
    elif last_name == "Möllemann" and first_names[0] == "Jürgen":
        first_names = ["Jürgen W."]
    elif last_name == "Kinkel" and first_names[0] == "Klaus":
        faction_override = "FDP"
        
    return first_names, faction_override

def find_matching_politician(
    politicians_df: pd.DataFrame,
    last_name: str,
    first_names: List[str],
    birth_date: int
) -> pd.DataFrame:
    """
    Find matching politician in the DataFrame based on name and birth date.
    
    Args:
        politicians_df (pd.DataFrame): DataFrame containing politicians data
        last_name (str): Last name to match
        first_names (List[str]): List of first names to match
        birth_date (int): Birth date to match
        
    Returns:
        pd.DataFrame: DataFrame containing matching politician(s) or empty DataFrame if none found
    """
    # Try matching with just the first name in the list
    birth_date_str = str(birth_date)
    possible_matches = politicians_df.loc[
        (politicians_df["last_name"] == last_name) &
        (politicians_df["first_name"].str.contains(first_names[0])) &
        (politicians_df["birth_date"].str.contains(birth_date_str))
    ]
    
    # Remove duplicates if any
    possible_matches = possible_matches.drop_duplicates(subset="ui", keep="first")
    
    # If no matches and there are multiple first names, try with complete first name
    if len(possible_matches) == 0 and len(first_names) > 1:
        full_first_name = " ".join([first_names[0], first_names[1]])
        possible_matches = politicians_df.loc[
            (politicians_df["last_name"] == last_name) &
            (politicians_df["first_name"] == full_first_name) &
            (politicians_df["birth_date"].str.contains(birth_date_str))
        ]
        possible_matches = possible_matches.drop_duplicates(subset="ui", keep="first")
    
    return possible_matches

def create_government_position_entry(
    politician_data: Dict[str, Any],
    electoral_term: int,
    faction_id: int,
    position: str
) -> Dict[str, Any]:
    """
    Create a dictionary entry for a government position.
    
    Args:
        politician_data (Dict[str, Any]): Base politician data
        electoral_term (int): Electoral term for this position
        faction_id (int): Faction ID for this position
        position (str): Government position title
        
    Returns:
        Dict[str, Any]: Dictionary with government position entry
    """
    # If politician_data is a Series (single politician match)
    if isinstance(politician_data, pd.Series):
        return {
            "ui": politician_data["ui"],
            "electoral_term": electoral_term,
            "faction_id": faction_id,
            "first_name": politician_data["first_name"],
            "last_name": politician_data["last_name"],
            "birth_place": politician_data["birth_place"],
            "birth_country": politician_data["birth_country"],
            "birth_date": politician_data["birth_date"],
            "death_date": politician_data["death_date"],
            "gender": politician_data["gender"],
            "profession": politician_data["profession"],
            "constituency": politician_data["constituency"],
            "aristocracy": politician_data["aristocracy"],
            "academic_title": politician_data["academic_title"],
            "institution_type": "Regierungsmitglied",
            "institution_name": position,
        }
    # If politician_data is a dict (new politician)
    else:
        return {
            "ui": politician_data["ui"],
            "electoral_term": electoral_term,
            "faction_id": faction_id,
            "first_name": politician_data["first_name"],
            "last_name": politician_data["last_name"],
            "birth_place": "",
            "birth_country": "",
            "birth_date": politician_data["birth_date"],
            "death_date": politician_data["death_date"],
            "gender": "",
            "profession": "",
            "constituency": "",
            "aristocracy": "",
            "academic_title": "",
            "institution_type": "Regierungsmitglied",
            "institution_name": position,
        }

def merge_government_members(
    politicians_df: pd.DataFrame, 
    mgs_df: pd.DataFrame, 
    factions_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge government members data into the politicians DataFrame.
    
    Args:
        politicians_df (pd.DataFrame): DataFrame containing MPs data
        mgs_df (pd.DataFrame): DataFrame containing government members data
        factions_df (pd.DataFrame): DataFrame containing factions data
        
    Returns:
        pd.DataFrame: Merged DataFrame containing all politicians
    """
    # Create a working copy of the politicians DataFrame
    result_df = politicians_df.copy()
    
    # Normalize hyphenated first names for better matching
    result_df["first_name"] = result_df["first_name"].str.replace("-", " ", regex=False)
    
    # Track statistics
    total_government_members = len(mgs_df)
    matched_to_existing = 0
    new_politicians = 0
    position_entries_added = 0
    
    logger.info("Starting merge of government members data into politicians data")
    
    # Iterate through government members
    for (
        last_name,
        first_name,
        birth_date,
        death_date,
        position,
        position_from,
        position_until,
        faction,
    ) in tqdm(
        zip(
            mgs_df["last_name"],
            mgs_df["first_name"],
            mgs_df["birth_date"],
            mgs_df["death_date"],
            mgs_df["position"],
            mgs_df["position_from"],
            mgs_df["position_until"],
            mgs_df["faction"],
        ),
        desc="Merging government members data...",
    ):
        try:
            # Handle special cases and correct names
            first_names = [first_name]  # Convert to list for processing
            first_names, faction_override = _fix_special_case_names(last_name, first_names)
            if faction_override:
                faction = faction_override
                
            # Normalize first names
            first_names = [normalize_name(name) for name in first_names]
            
            # Match faction name to standardized abbreviation
            faction_abbrev = get_faction_abbrev(faction, FACTION_PATTERNS)
            
            # Get faction ID
            if faction_abbrev:
                try:
                    faction_match = int(
                        factions_df.loc[factions_df["abbreviation"] == faction_abbrev, "id"].iloc[0]
                    )
                except (IndexError, KeyError):
                    logger.warning(f"Could not find faction ID for abbreviation: {faction_abbrev}")
                    faction_match = -1
            else:
                logger.warning(f"Could not match faction name: {faction}")
                faction_match = -1
            
            # Determine electoral terms for this position
            try:
                electoral_terms = get_electoral_term(
                    from_year=int(position_from), to_year=int(position_until)
                )
                # Make sure we have a list of terms
                if not isinstance(electoral_terms, list):
                    electoral_terms = [electoral_terms]
            except (ValueError, AttributeError) as e:
                logger.error(f"Error determining electoral terms for position {position}: {e}")
                continue
            
            # Find matching politician in existing data
            possible_matches = find_matching_politician(
                result_df, last_name, first_names, birth_date
            )
            
            # Case 1: Found exactly one match - use existing politician record
            if len(possible_matches) == 1:
                matched_to_existing += 1
                politician_data = possible_matches.iloc[0]
                
                # Add position entry for each electoral term
                for electoral_term in electoral_terms:
                    entry = create_government_position_entry(
                        politician_data, electoral_term, faction_match, position
                    )
                    entry_df = pd.DataFrame(entry, index=[result_df.index[-1]])
                    result_df = pd.concat([result_df, entry_df], ignore_index=True)
                    position_entries_added += 1
                    
            # Case 2: Multiple matches (shouldn't happen with current logic)
            elif len(possible_matches) > 1:
                logger.warning(f"Multiple matches found for {' '.join(first_names)} {last_name}")
                # Use the first match
                politician_data = possible_matches.iloc[0]
                
                # Add position entry for each electoral term
                for electoral_term in electoral_terms:
                    entry = create_government_position_entry(
                        politician_data, electoral_term, faction_match, position
                    )
                    entry_df = pd.DataFrame(entry, index=[result_df.index[-1]])
                    result_df = pd.concat([result_df, entry_df], ignore_index=True)
                    position_entries_added += 1
                    
            # Case 3: No match found - create new politician entry
            else:
                new_politicians += 1
                # Generate new unique ID
                new_ui = max(result_df["ui"].astype(str).tolist()) + 1
                
                # Basic politician data
                politician_data = {
                    "ui": new_ui,
                    "first_name": " ".join(first_names),
                    "last_name": last_name,
                    "birth_date": str(birth_date),
                    "death_date": str(death_date),
                }
                
                # Add position entry for each electoral term
                for electoral_term in electoral_terms:
                    entry = create_government_position_entry(
                        politician_data, electoral_term, faction_match, position
                    )
                    entry_df = pd.DataFrame(entry, index=[result_df.index[-1]])
                    result_df = pd.concat([result_df, entry_df], ignore_index=True)
                    position_entries_added += 1
                    
        except Exception as e:
            logger.error(f"Error processing government member {first_name} {last_name}: {e}")
            continue
            
    # Log merge statistics
    logger.info(f"Merged {total_government_members} government members:")
    logger.info(f" - {matched_to_existing} matched to existing politicians")
    logger.info(f" - {new_politicians} new politicians created")
    logger.info(f" - {position_entries_added} government position entries added")
    
    return result_df

def main(task) -> bool:
    """
    Main function that orchestrates loading data, merging politicians,
    and saving the merged data.
    
    Args:
        task: The doit task object (not used, but required for doit compatibility)
        
    Returns:
        bool: True for success, False for failure
    """
    # Define input/output paths
    MGS_PATH = path.POLITICIANS_STAGE_01
    MPS_PATH = path.POLITICIANS_STAGE_02
    FACTIONS_PATH = path.DATA_FINAL
    
    # Step 1: Load the required data
    mps_df, mgs_df, factions_df = load_politicians_data(MPS_PATH, MGS_PATH, FACTIONS_PATH)
    if mps_df is None or mgs_df is None or factions_df is None:
        logger.error("Failed to load required data, exiting")
        return False
    
    # Step 2: Merge government members data into politicians data
    try:
        merged_politicians = merge_government_members(mps_df, mgs_df, factions_df)
        logger.info(f"Successfully merged politicians data, final size: {len(merged_politicians)} records")
    except Exception as e:
        logger.error(f"Error merging politicians data: {e}")
        return False
    
    # Step 3: Save the merged data
    output_file = FACTIONS_PATH / "politicians.csv"
    try:
        merged_politicians.to_csv(output_file, index=False)
        logger.info(f"Successfully saved merged politicians data to {output_file}")
    except Exception as e:
        logger.error(f"Error saving merged politicians data: {e}")
        return False
    
    logger.info("Script completed: merge_politicians done.")
    return True