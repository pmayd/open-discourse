"""
Functions for step02 function 01_split_xml
"""

import logging
import xml.etree.ElementTree as Et
from pathlib import Path
from xml.etree.ElementTree import ParseError

import regex

# use predefined logger
logger = logging.getLogger()


def split_single_session_xml_data(xml_file_path: Path) -> tuple:
    """
    Open a session protocol xml-file and split content into metadata and text corpus.
    Raise ParseError resp. ValueError when xml-content cannot be processed properly
    or expected tags are missing.

    Args:
        xml_file_path (Path): Path to single session protocol xml-file

    Returns:
        meta_data (dict):   Metadata of current xml-file
        text_corpus (str):  Content of tag <TEXT> of current xml-file
    """

    # Cancel if not xml file, this case should not occur
    if (not xml_file_path.is_file()) or xml_file_path.suffix != ".xml":
        msg = f"xml file expected {xml_file_path}"
        raise FileNotFoundError(msg)

    meta_data = {}
    text_corpus = None

    try:
        tree = Et.parse(xml_file_path)
    except ParseError:
        msg = "xml ParseError" + str(xml_file_path)
        logger.error(msg)
        raise

    try:
        meta_data["term"] = tree.find("WAHLPERIODE").text
        meta_data["document_type"] = tree.find("DOKUMENTART").text
        # Get the document number, the date of the session and the content.
        meta_data["document_number"] = tree.find("NR").text
        meta_data["date"] = tree.find("DATUM").text
        text_corpus = tree.find("TEXT").text
    except AttributeError:
        msg = "xml AttributeError" + str(xml_file_path)
        logger.error(msg)
        raise

    # Are filename and meta_data consistent?
    if (
        xml_file_path.stem != f"{int(meta_data["term"]):02d}"
        f"{int(meta_data["document_number"].split("/")[1]):03d}"
    ):
        msg = (
            f"meta_data / filepath not consistent: {str(xml_file_path)} "
            f"{meta_data["document_number"]}"
        )
        logger.warning(msg)

    return meta_data, text_corpus


def define_single_session_regex_pattern(meta_data: dict) -> tuple:
    """
    Define regex pattern for finding begin of speech_content respectively appendix
    of a session protocol.
    Based on a standard case, various exceptions from
    individual protocols (based on meta_data["document_number"]) are taken into account.

    Args:
        meta_data (dict):   Metadata of current xml-file

    Returns:
        begin_pattern (compiled regex):     regex pattern for begin of speech content
        appendix_pattern (compiled regex):  regex pattern for appendix

    """
    begin_pattern_electoral_term = r"Beginn?:?\s?(\d){1,2}(\s?[.,]\s?(\d){1,2})?\s?Uhr"
    appendix_pattern_electoral_term = (
        r"\(Schlu(ß|ss)\s?:?(.*?)\d{1,2}\D+(\d{1,"
        r"2})?(.*?)\)?|\(Ende der Sitzung: \d{1,"
        r"2}\D+(\d{1,2}) Uhr\.?\)"
    )

    begin_pattern = begin_pattern_electoral_term
    appendix_pattern = appendix_pattern_electoral_term

    # Some files have issues which have to be handled manually
    # like a duplicated text corpus or two sessions in one file.
    # change begin_pattern / appendix_patern only when different to default
    if meta_data["document_number"] == "03/16":
        appendix_pattern = r"\(Schluß der Sitzung: 16\.58 Uhr\.\)"
    elif meta_data["document_number"] == "04/69":
        begin_pattern = r"Beginn: 9\.01"
    elif meta_data["document_number"] == "04/176":
        begin_pattern = r"Beginn: 16\.02 Uhr"
    elif meta_data["document_number"] == "04/196":
        appendix_pattern = r"Beifall.*?Schluß der Sitzung: 14\.54 Uhr\.\)"
    elif meta_data["document_number"] == "05/76":
        begin_pattern = r"\(Beginn: 14\.32 Uhr\)"
    elif meta_data["document_number"] == "05/162":
        begin_pattern = r"\(Beginn: 21\.13 Uhr\.\)"
    elif meta_data["document_number"] == "05/235":
        appendix_pattern = r"\(Schluß der Sitzung: 16\.09 Uhr\.\)"
    elif meta_data["document_number"] == "07/243":
        begin_pattern = r"Beginn: 9\.00 Uhr(?=\nPräsident)"
    elif meta_data["document_number"] == "08/7":
        begin_pattern = r"Beginn: 9\.00 Uhr(?=\nPräsident)"
    elif meta_data["document_number"] == "08/146":
        begin_pattern = r"Beginn: 8\.00 Uhr"
    elif meta_data["document_number"] == "11/68":
        appendix_pattern = r"\(Schluß der Sitzung: 21\. 07 Uhr\)"
    elif meta_data["document_number"] == "11/155":
        begin_pattern = r"Beginn: 9\.00 Uhr(?=\nVize)"
    elif meta_data["document_number"] == "14/17":
        begin_pattern = "Beginn: 9.00 Uhr"
        appendix_pattern = (
            r"Schluß: 12.06 Uhr\)\n\nDruck: Bonner Universitäts-Buchdruckerei, 53113 "
            r"Bonn\n 53003 Bonn, Telefon: 02 28/3 82 08 40, Telefax: 02 28/3 82 08 "
            r"44\n\n20\n\nBundespräsident Dr. Roman Herzog\n\nDeutscher"
        )
    elif meta_data["document_number"] == "14/21":
        appendix_pattern = r"\(Schluß: 22.18 Uhr\)\n\nAdelheid Tröscher\n\n1594"
    elif meta_data["document_number"] == "14/192":
        appendix_pattern = r"Vizepräsidentin Petra Bläss: Ich schließe die "
        appendix_pattern += r"Aus-\nsprache\.(?=\n\nInter)"
    elif meta_data["document_number"] == "16/222":
        appendix_pattern = r"\(Schluss: 18\.54 Uhr\)"
    elif meta_data["document_number"] == "17/250":
        begin_pattern = r"Beginn: 9.02 Uhr(?=\nPräsident)"
        appendix_pattern = r"\(Schluss: 0.52 Uhr\)\n\nIch"
    elif meta_data["document_number"] == "18/142":
        appendix_pattern = r"\(Schluss: 16 \.36 Uhr\)"
    elif meta_data["document_number"] == "18/237":
        begin_pattern = r"Beginn: 9 \.02 Uhr"

    # return compiled regex
    begin_pattern = regex.compile(begin_pattern)
    appendix_pattern = regex.compile(appendix_pattern)

    return begin_pattern, appendix_pattern


def single_session_special_text_split(meta_data: dict, text_corpus: str) -> str:
    """
    Change the content of text_corpus for some special cases (e.g. duplicated text
    corpus or two sessions in one protocol),
    dependent from meta_data["document_number"].
    In the standard case, text_corpus is returned unchanged.

    Args:
        meta_data (dict):   Metadata of current xml-file
        text_corpus (str):  Content of tag <TEXT> of current xml-file

    Returns:
        text_corpus (str):  Improved content of tag <TEXT> of current xml-file

    """
    # Some files have issues which have to be handled manually
    # like a duplicated text corpus or two sessions in one file.
    if meta_data["document_number"] == "07/145":
        # In this file the whole text is duplicated.
        find_bundestag = list(regex.finditer("Deutscher Bundestag\n", text_corpus))
        text_corpus = text_corpus[: find_bundestag[1].span()[0]]
    elif meta_data["document_number"] in [
        "03/97",
        "04/66",
        "04/87",
        "04/112",
        "05/47",
        "05/232",
    ]:
        # In these documents there are two sessions right after each
        # other, and the following document is identical.
        find_second = regex.search(
            "(?<=\n)"
            + str(int(meta_data["document_number"][3:]) + 1)
            + r"\. Sitzung(?=\nBonn)",
            text_corpus,
        )
        text_corpus = text_corpus[: find_second.span()[0]]
    elif meta_data["document_number"] in [
        "03/98",
        "04/67",
        "04/88",
        "04/113",
        "05/48",
        "05/233",
    ]:
        find_second = regex.search(
            "(?<=\n)" + meta_data["document_number"][3:] + r"\. Sitzung(?=\nBonn)",
            text_corpus,
        )
        text_corpus = text_corpus[find_second.span()[0] :]

    return text_corpus
