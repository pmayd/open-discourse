# Standardbibliotheken
from datetime import datetime

# Drittanbieterbibliotheken
import pandas as pd

# Eigene Module
import open_discourse.definitions.path_definitions as path_definitions
import logging


logger = logging.getLogger()

# Output directory
# ELECTORAL_TERMS = path_definitions.ELECTORAL_TERMS
# ELECTORAL_TERMS.mkdir(parents=True, exist_ok=True)

# To validate output we use the synchro_dir
ELECTORAL_TERMS = path_definitions.SYNCHRO_DIR / "electoral_terms_synchro"
ELECTORAL_TERMS.mkdir(parents=True, exist_ok=True)

# Dates
electoral_terms = [
    {"start_date": "1949-09-07", "end_date": "1953-10-05"},
    {"start_date": "1953-10-06", "end_date": "1957-10-14"},
    {"start_date": "1957-10-15", "end_date": "1961-10-16"},
    {"start_date": "1961-10-17", "end_date": "1965-10-18"},
    {"start_date": "1965-10-19", "end_date": "1969-10-19"},
    {"start_date": "1969-10-20", "end_date": "1972-12-12"},
    {"start_date": "1972-12-13", "end_date": "1976-12-13"},
    {"start_date": "1976-12-14", "end_date": "1980-11-03"},
    {"start_date": "1980-11-04", "end_date": "1983-03-28"},
    {"start_date": "1983-03-29", "end_date": "1987-02-17"},
    {"start_date": "1987-02-18", "end_date": "1990-12-19"},
    {"start_date": "1990-12-20", "end_date": "1994-11-09"},
    {"start_date": "1994-11-10", "end_date": "1998-10-25"},
    {"start_date": "1998-10-26", "end_date": "2002-10-16"},
    {"start_date": "2002-10-17", "end_date": "2005-10-17"},
    {"start_date": "2005-10-18", "end_date": "2009-10-26"},
    {"start_date": "2009-10-27", "end_date": "2013-10-21"},
    {"start_date": "2013-10-22", "end_date": "2017-10-23"},
    {"start_date": "2017-10-24", "end_date": "2021-10-26"},
    {"start_date": "2021-10-27", "end_date": "2025-10-29"},
]



# Functions
def convert_date_to_delta_seconds(
    date_string, ref_date=datetime(year=1970, month=1, day=1)
):
    """
    Konvertiert ein Datum im Format "YYYY-MM-DD" in ein `datetime`-Objekt,
    berechnet die Differenz (delta) zum Referenzdatum und gibt diese Differenz in Sekunden zurück.

    Args:
        date_string (str): Ein Datum als String im Format "YYYY-MM-DD".
        ref_date (datetime): Das Referenzdatum als `datetime`-Objekt.

    Returns:
        float: Die Differenz zwischen `date_string` und `ref_date` in Sekunden.

    Raises:
        ValueError: Wenn der `date_string` nicht im Format "YYYY-MM-DD" ist.
    """
    date = datetime.strptime(date_string, "%Y-%m-%d")
    return (date - ref_date).total_seconds()


def convert_electoral_term_dates(electoral_terms):
    """
    Konvertiert die Start- und End-Daten jeder Wahlperiode in Sekunden.

    Args:
        electoral_terms (list[dict]): Eine Liste von Dictionaries mit Datumseinträgen.

    Returns:
        list[dict]: Eine Liste von Dictionaries mit konvertierten Werten.
    """
    if not electoral_terms:
        logger.error("List of electoral terms not found or is empty.")
        return []

    converted_terms = []
    for index, term in enumerate(electoral_terms):
        try:
            converted_term = {
                key: convert_date_to_delta_seconds(date_string)
                for key, date_string in term.items()
            }

            converted_terms.append(converted_term)

        except Exception as e:
            logger.error(
                f"Error processing term at index {index}: {term}. Exception: {e}"
            )

    if not converted_terms:
        logger.warning("No electoral terms could be converted successfully.")

    return converted_terms


def add_ids(electoral_terms):
    """
    Fügt jedem Dictionary in der Liste eine eindeutige ID hinzu.

    Args:
        electoral_terms (list[dict]): Eine Liste von Dictionaries.

    Returns:
        list[dict]: Eine Liste von Dictionaries mit einer zusätzlichen ID.
    """
    for idx, term in enumerate(electoral_terms):
        term["id"] = idx + 1
    logger.debug("add_ids succesful")

    return electoral_terms


def save_as_csv(electoral_terms):
    # Referenzdatum, gegen das die Differenz in Sekunden berechnet wird
    save_path = ELECTORAL_TERMS / "electoral_terms.csv"

    pd.DataFrame(electoral_terms).to_csv(save_path, index=False)
    logger.debug("save_as_csv succesful")
