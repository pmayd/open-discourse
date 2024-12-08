import copy
import logging
import xml.etree.ElementTree as Et

# use predefined logger
logger = logging.getLogger()


# placeholder for final dataframe
mps_init = {
    "ui": [],
    "electoral_term": [],
    "first_name": [],  # VORNAME,
    "last_name": [],  # NACHNAME,
    "birth_place": [],  # GEBURTSORT
    "birth_country": [],  # GEBURTSLAND
    "birth_date": [],  # GEBURTSDATUM
    "death_date": [],  # STERBEDATUM
    "gender": [],  # GESCHLECHT
    "profession": [],  # BERUF
    "constituency": [],  # ORTSZUSATZ,
    "aristocracy": [],  # ADEL,
    "academic_title": [],  # AKAD_TITEL,
    "institution_type": [],  # INSART_LANG
    "institution_name": [],  # INS_LANG
}


def process_single_mdb(xml_mdb: Et.Element) -> dict:
    """
    Processes xml-data of one MP (MdB) and returns dict with the desired subset of data

    Args:
        xml_mdb (Et.Element):   xml-data of one MP (MdB)

    Returns:
        mps (dict):         dict with data of one MP (MdB)
    """
    mps = copy.deepcopy(mps_init)  # Empty dict
    mdb = xml_mdb

    ui = mdb.findtext("ID")
    # This entries exist only once for every politician.
    if mdb.findtext("BIOGRAFISCHE_ANGABEN/GEBURTSDATUM") == "":
        msg = f"birth_date missing for id {ui}"
        logger.error(msg)
        birth_date = -1
    else:
        birth_date = str(mdb.findtext("BIOGRAFISCHE_ANGABEN/GEBURTSDATUM"))

    birth_place = mdb.findtext("BIOGRAFISCHE_ANGABEN/GEBURTSORT")
    birth_country = mdb.findtext("BIOGRAFISCHE_ANGABEN/GEBURTSLAND")
    if birth_country == "":
        birth_country = "Deutschland"

    if mdb.findtext("BIOGRAFISCHE_ANGABEN/STERBEDATUM") == "":
        death_date = -1
    else:
        death_date = str(mdb.findtext("BIOGRAFISCHE_ANGABEN/STERBEDATUM"))

    gender = mdb.findtext("BIOGRAFISCHE_ANGABEN/GESCHLECHT")
    profession = mdb.findtext("BIOGRAFISCHE_ANGABEN/BERUF")

    # Iterate over all name entries for the poltiician_id, e.g. necessary if
    # name has changed due to a marriage or losing/gaining of titles like "Dr."
    # Or if in another period the location information
    # changed "" -> "Bremerhaven"
    for name in mdb.findall("./NAMEN/NAME"):
        first_name = name.findtext("VORNAME")
        last_name = name.findtext("NACHNAME")
        constituency = name.findtext("ORTSZUSATZ")
        aristocracy = name.findtext("ADEL")
        academic_title = name.findtext("AKAD_TITEL")

        # Hardcode Schmidt (Weilburg). Note: This makes 4 entries for
        # Frank Schmidt!!
        # if regex.search(r"\(Weilburg\)", last_name):
        if "(Weilburg)" in last_name:
            last_name = last_name.replace(" (Weilburg)", "")
            constituency = "(Weilburg)"

        # Iterate over parliament periods the politician was member
        # of the Bundestag.
        for electoral_term in mdb.findall("./WAHLPERIODEN/WAHLPERIODE"):
            electoral_term_number = electoral_term.findtext("WP")

            # Iterate over faction membership in each parliament period, e.g.
            # multiple entries exist if faction was changed within period.
            for institution in electoral_term.findall("./INSTITUTIONEN/INSTITUTION"):
                institution_name = institution.findtext("INS_LANG")
                institution_type = institution.findtext("INSART_LANG")

                mps["ui"].append(ui)
                mps["electoral_term"].append(electoral_term_number)
                mps["first_name"].append(first_name)
                mps["last_name"].append(last_name)
                mps["birth_place"].append(birth_place)
                mps["birth_country"].append(birth_country)
                mps["birth_date"].append(birth_date)
                mps["death_date"].append(death_date)
                mps["gender"].append(gender)
                mps["profession"].append(profession)
                mps["constituency"].append(constituency)
                mps["aristocracy"].append(aristocracy)
                mps["academic_title"].append(academic_title)

                mps["institution_type"].append(institution_type)
                mps["institution_name"].append(institution_name)

    return mps
