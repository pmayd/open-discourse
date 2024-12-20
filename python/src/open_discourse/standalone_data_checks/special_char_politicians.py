import csv
import logging

import regex

import open_discourse.definitions.path_definitions as path_definitions

VALID_CHARS = r"[a-zäöüßA-ZÄÖÜ0-9 \-\.]"


def get_politicians_with_special_chars():
    """
    Get first and last names of politicians with special chars from final file
    'politicians.csv'. This file must already exist!
    Special chars are those who are not defined in VALID_CHARS.

    Returns:
        sorted list: All names with special chars, regardless of first or last name
    """
    # todo pytest

    # Initialize empty list
    csv_liste = []
    filepath = path_definitions.FINAL / "politicians.csv"
    assert filepath.exists(), f"file {filepath} doesn't exist!"

    # open csv-file with final politicians
    with open(filepath, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)  # DictReader reads csv with column names

        for row in reader:
            # Build one list with all first and last names
            csv_liste.append(row["first_name"])
            csv_liste.append(row["last_name"])

    # compress the list (no duplicates)
    csv_liste = list(set(csv_liste))

    # compile regex pattern to find chars that are NOT in VALID_CHARS
    regpat = regex.compile(f"[^{VALID_CHARS[1:-1]}]")

    # check every entry in csv_liste
    politicians_with_special_chars = [s for s in csv_liste if regpat.search(s)]

    result_len = len(politicians_with_special_chars)
    msg = (
        f"{result_len} politicians_with_special_chars found,"
        f"starting with {politicians_with_special_chars[0]}"
    )
    logging.debug(msg)

    # MDB_STAMMDATEN.XML in 2024 contains at least 13 different names wih special chars
    assert result_len >= 13, "Too few politicians with special chars found"

    return sorted(politicians_with_special_chars)

result = get_politicians_with_special_chars()
print(f"Found {len(result)} politicians with special chars:")
print(result)
