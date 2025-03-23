"""
Script to scrape Wikipedia for German government members data since 1949.

This script is part of the Open Discourse data processing pipeline and performs the following tasks:
1. Retrieves the Wikipedia page listing German government members since 1949
2. Parses the HTML to extract politician information (names, positions, dates, party affiliations)
3. Structures the data into a pandas DataFrame
4. Saves the government members data for further processing in the politicians pipeline
"""

import pandas as pd
import regex
import requests
from bs4 import BeautifulSoup
from typing import Tuple, Optional

# Project-specific imports
from open_discourse.definitions import path
from open_discourse.helper.logging_config import setup_and_get_logger
from open_discourse.helper.io_utils import save_pickle

# Constants
WIKIPEDIA_URL = (
    "https://de.wikipedia.org/wiki/Liste_der_deutschen_Regierungsmitglieder_seit_1949"
)
DEFAULT_VALUE = -1  # Value used when a date is unknown

# Configure a logger for this script
logger = setup_and_get_logger("scrape_government_members")


def fetch_wikipedia_content(url: str) -> Optional[BeautifulSoup]:
    """
    Fetch and parse Wikipedia page content.

    Args:
        url (str): URL of the Wikipedia page to fetch

    Returns:
        Optional[BeautifulSoup]: Parsed BeautifulSoup object containing the main content section,
                              or None if fetching or parsing failed
    """
    try:
        logger.info(f"Fetching content from {url}")
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses

        soup = BeautifulSoup(response.text, "html.parser")
        main_section = soup.find("div", {"id": "mw-content-text"})

        if main_section is None:
            logger.error("Could not find main content section on Wikipedia page")
            return None

        content_div = main_section.find("div")
        if content_div is None:
            logger.error("Could not find content div within main section")
            return None

        return content_div

    except requests.RequestException as e:
        logger.error(f"Error fetching Wikipedia page: {e}")
        return None
    except Exception as e:
        logger.error(f"Error parsing Wikipedia content: {e}")
        return None


def extract_birth_death_years(birth_death_text: str) -> Tuple[int, int]:
    """
    Extract birth and death years from a text string.

    Args:
        birth_death_text (str): Text containing birth and possibly death years

    Returns:
        Tuple[int, int]: Tuple containing (birth_year, death_year), with death_year as DEFAULT_VALUE if not present
    """
    match_years = regex.findall(r"(\d{4})", birth_death_text)

    if len(match_years) == 1:  # Only birth year
        return int(match_years[0]), DEFAULT_VALUE
    elif len(match_years) == 2:  # Birth and death years
        return int(match_years[0]), int(match_years[1])
    else:  # Unknown
        return DEFAULT_VALUE, DEFAULT_VALUE


def parse_government_position(position_text: str) -> Tuple[Optional[str], int, int]:
    """
    Parse a government position entry to extract position title and years.

    Args:
        position_text (str): Text describing a government position with years

    Returns:
        Tuple[Optional[str], int, int]: Tuple of (position_title, from_year, until_year)

    Raises:
        ValueError: If the position text has an unexpected format
    """
    match_years = regex.findall(r"(\d{4})", position_text)

    if len(match_years) == 2:
        # Example: "1974–1980 Verkehr und Post- und Fernmeldewesen"
        position_from = int(match_years[0])
        position_until = int(match_years[1])

        position_full = position_text.split(" ", 1)
        if len(position_full) == 2:
            position = position_full[1]
            return position, position_from, position_until
        else:
            raise ValueError(f"Cannot extract position title from: {position_text}")

    elif len(match_years) == 1:
        if "seit" in position_text:
            # Example: "seit 2018 Arbeit und Soziales"
            position_from = int(match_years[0])
            position_until = DEFAULT_VALUE

            parts = position_text.split(" ", 1)[1].split(" ", 1)
            if len(parts) > 1:
                position = parts[1]
                return position, position_from, position_until
            else:
                raise ValueError(f"Cannot extract position title from: {position_text}")
        else:
            # Example: "1969 Justiz"
            parts = position_text.split(" ", 1)
            if len(parts) > 1:
                position = parts[1]
                position_from = position_until = int(match_years[0])
                return position, position_from, position_until
            else:
                raise ValueError(f"Cannot extract position title from: {position_text}")

    elif len(match_years) == 4:
        # Example: "1969–1982, 1982–1983 Keks Beauftragter"
        # Split on comma and spaces
        title_part = position_text.split(" ", 1)[1].split(" ", 1)
        if len(title_part) > 1:
            position = title_part[1]
            # Return first term
            position_from1 = int(match_years[0])
            position_until1 = int(match_years[1])
            # Store second term for caller to add separately
            position_from2 = int(match_years[2])
            position_until2 = int(match_years[3])
            return (
                position,
                position_from1,
                position_until1,
                position_from2,
                position_until2,
            )
        else:
            raise ValueError(
                f"Cannot extract position title from multiple terms: {position_text}"
            )
    else:
        raise ValueError(f"Unexpected number of years in position: {position_text}")


def extract_politician_data(content_div: BeautifulSoup) -> pd.DataFrame:
    """
    Extract politician data from the parsed Wikipedia content.

    Args:
        content_div (BeautifulSoup): BeautifulSoup object containing the main content with politician data

    Returns:
        pd.DataFrame: DataFrame containing the extracted politician information
    """
    # Initialize data structure
    politicians_data = {
        "ui": [],
        "last_name": [],
        "first_name": [],
        "position": [],
        "position_from": [],
        "position_until": [],
        "birth_date": [],
        "death_date": [],
        "faction": [],
        "additional_faction": [],
    }

    ui_counter = 0

    logger.info("Starting extraction of politician data from Wikipedia content")

    try:
        for div in content_div.find_all("div", recursive=False):
            for ul in div.find_all("ul", recursive=False):
                for li in ul.find_all("li", recursive=False):
                    try:
                        # Extract politician's basic information
                        find_all_a = li.find_all("a", recursive=False)
                        if not find_all_a:
                            logger.warning("Found list item without links, skipping")
                            continue

                        name = find_all_a[0].text

                        # Skip some special entries that aren't politicians
                        if "Liste" in name or "Kabinett" in name:
                            logger.debug(f"Skipping non-politician entry: {name}")
                            break

                        # Skip problematic entry (special case handling)
                        if "CDU" in name:
                            logger.debug(
                                f"Skipping problematic entry with 'CDU' in name: {name}"
                            )
                            continue

                        # Parse name into first and last name
                        name_parts = name.split(" ")
                        first_name = " ".join(name_parts[:-1])
                        last_name = name_parts[-1]

                        # Extract faction (party) information
                        if len(find_all_a) > 2:
                            faction = find_all_a[1].text
                            additional_faction = find_all_a[2].text
                        elif len(find_all_a) == 2:
                            faction = find_all_a[1].text
                            additional_faction = ""
                        else:
                            faction = "parteilos"
                            additional_faction = ""

                        # Extract birth/death information
                        birth_death_text = li.a.next_sibling.strip()
                        birth_date, death_date = extract_birth_death_years(
                            birth_death_text
                        )

                        # Process each government position for this politician
                        positions_list = li.find_all("li")
                        if not positions_list:
                            logger.warning(
                                f"No positions found for {first_name} {last_name}, skipping"
                            )
                            continue

                        for pos_item in positions_list:
                            pos_text = pos_item.text
                            try:
                                # Parse the position information
                                result = parse_government_position(pos_text)

                                # Check if we have a position with two terms (4 years extracted)
                                if len(result) == 5:
                                    (
                                        position,
                                        pos_from1,
                                        pos_until1,
                                        pos_from2,
                                        pos_until2,
                                    ) = result

                                    # Add the first term
                                    politicians_data["ui"].append(f"gov_{ui_counter}")
                                    politicians_data["first_name"].append(first_name)
                                    politicians_data["last_name"].append(last_name)
                                    politicians_data["position"].append(position)
                                    politicians_data["position_from"].append(pos_from1)
                                    politicians_data["position_until"].append(
                                        pos_until1
                                    )
                                    politicians_data["birth_date"].append(birth_date)
                                    politicians_data["death_date"].append(death_date)
                                    politicians_data["faction"].append(faction)
                                    politicians_data["additional_faction"].append(
                                        additional_faction
                                    )

                                    # The second term will be added in the common block below
                                    position_from = pos_from2
                                    position_until = pos_until2

                                else:
                                    position, position_from, position_until = result

                                # Add the position entry
                                politicians_data["ui"].append(f"gov_{ui_counter}")
                                politicians_data["first_name"].append(first_name)
                                politicians_data["last_name"].append(last_name)
                                politicians_data["position"].append(position)
                                politicians_data["position_from"].append(position_from)
                                politicians_data["position_until"].append(
                                    position_until
                                )
                                politicians_data["birth_date"].append(birth_date)
                                politicians_data["death_date"].append(death_date)
                                politicians_data["faction"].append(faction)
                                politicians_data["additional_faction"].append(
                                    additional_faction
                                )

                            except ValueError as e:
                                logger.error(
                                    f"Error parsing position for {first_name} {last_name}: {e}"
                                )
                                continue

                        ui_counter += 1

                    except Exception as e:
                        logger.error(f"Error processing politician entry: {e}")
                        continue

    except Exception as e:
        logger.error(f"Error processing Wikipedia content: {e}")

    # Convert to DataFrame
    politicians_df = pd.DataFrame(politicians_data)

    # Log extraction statistics
    unique_politicians = politicians_df["ui"].nunique()
    total_positions = len(politicians_df)
    logger.info(
        f"Extracted data for {unique_politicians} politicians with {total_positions} government positions"
    )

    return politicians_df


def main(task) -> bool:
    """
    Main function that orchestrates the Wikipedia scraping process
    and saves the extracted government members data.

    Args:
        task: The doit task object (not used, but required for doit compatibility)

    Returns:
        bool: True for success, False for failure
    """
    # Define output path
    POLITICIANS_STAGE_01 = path.POLITICIANS_STAGE_01
    POLITICIANS_STAGE_01.mkdir(parents=True, exist_ok=True)

    # Step 1: Fetch Wikipedia content
    content_div = fetch_wikipedia_content(WIKIPEDIA_URL)
    if content_div is None:
        logger.error("Failed to fetch or parse Wikipedia content")
        return False

    # Step 2: Extract politician data
    try:
        politicians_df = extract_politician_data(content_div)
        if politicians_df.empty:
            logger.error(
                "Failed to extract politicians data, resulting DataFrame is empty"
            )
            return False
    except Exception as e:
        logger.error(f"Error extracting politicians data: {e}")
        return False

    # Step 3: Save the extracted data
    output_file = POLITICIANS_STAGE_01 / "mgs.pkl"
    if not save_pickle(politicians_df, output_file, logger):
        return False

    logger.info("Script completed: scrape_mgs done.")
    return True
