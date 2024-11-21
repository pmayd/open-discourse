import logging
import xml.etree.ElementTree as Et
from pathlib import Path
from xml.etree.ElementTree import ParseError

import dicttoxml
import regex
from tqdm import tqdm

import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.helper_functions.clean_text import clean
from open_discourse.helper_functions.utils import get_term_from_path


# use predefined logger
logger = logging.getLogger()

### KONSTANTEN
# input directory
RAW_XML = path_definitions.RAW_XML

# output directory
RAW_TXT = path_definitions.RAW_TXT
RAW_TXT.mkdir(parents=True, exist_ok=True)

SESSIONS_PER_TERM = {1: 282, 2: 227, 3: 168, 4: 198, 5: 247, 6: 199, 7: 259, 8: 230, 9: 142, 10: 256,
                     11: 236, 12: 243, 13: 248, 14: 253, 15: 187, 16: 233, 17: 253, 18: 245, 19: 239}


def pp_iterate_03_to_19(source_dir: Path, target_dir: Path, term: int | None = None,
                        session: int | None = None) -> object:
    """
    Iterates through every subfolder of source_dir, e.g. RAW_XML
    and calls processing function for single file: pp_process_single_session

    Args:
        source_dir (Path):
        target_dir (Path):
        term (int):         legislative term
        session (int):      session number in legislative term

    Returns:
        None
    """
    logger.debug(f"Script pp_iterate_03_to_19 starts")
    # Check args
    if source_dir != RAW_XML:
        raise NotImplementedError("Nur RAW_XML als Eingabe zulässig")
    else:
        input_suffix = ".xml"
    assert source_dir.exists(), f"Output directory {source_dir} does not exist."
    if target_dir != RAW_TXT:
        raise NotImplementedError("Nur RAW_TXT als Ausgabe zulässig")
    else:
        output_suffix = ".txt"
    assert target_dir.exists(), f"Output directory {target_dir} does not exist."
    if term and not 3 <= term <= 19:
        msg = f"Invalid arg: term {term}"
        raise ValueError(msg)
    if session:
        if not term:
            msg = f"Invalid arg: term must be set when session {session} is set"
            raise ValueError(msg)
        elif not 1 <= session <= SESSIONS_PER_TERM[term]:
            msg = f"Invalid arg: term {term}"
            raise ValueError(msg)

    ### Iterate through every input planar file in every legislature term, unless term and/or session are explicitly stated

    # Open every sub_directory of source_dir
    for folder_path in sorted(source_dir.iterdir()):
        # Skip e.g. the .DS_Store file.
        if not folder_path.is_dir():
            continue

        term_number = get_term_from_path(str(folder_path))
        if term_number is None:
            logger.debug(f"No term number found in {folder_path.stem}.")
            continue

        # Don't process sub_directories outside scope of this function, that is term 3 to 19 or term in args
        if not (3 <= term_number <= 19) or (term and term != term_number):
            continue

        # Process all relevant files in sub_directory
        # session from args, so only one input file
        if session is not None:
            input_files = list(Path(folder_path).glob(f"{term:02d}{session:03d}{input_suffix}"))
            assert len(input_files) == 1
        # all sessions in sub_directory
        else:
            input_files = list(folder_path.glob("*" + input_suffix))
            assert len(input_files) == SESSIONS_PER_TERM[term_number]

        for input_file_path in tqdm(input_files, desc=f"Parsing term {term_number:>2}..."):
            pp_process_single_session(input_file_path, folder_path)

        # assert RAW_TXT.exists(), f"Output directory {RAW_TXT}does not exist."
        # assert len(list(RAW_TXT.glob("*_pp*"))) == 19 - 3 + 1

    return


def pp_process_single_session(input_file_path: Path, folder_path: Path) -> object:
    """
    Cleans and split a single plenar protocol to
    - TOC
    - Session content
    - Appendix
    - metadate
    and write 4 files.

    Args:
        input_file_path (Path): single session protocol file to be orocessed
        folder_path (Path):     folder_path for output

    Returns:

    """
    # 1 split xml
    try:
        meta_data, text_corpus = pp_split_xml_data(input_file_path)
    except ParseError:
        return

    # 2 regex patterns
    begin_pattern, appendix_pattern = pp_define_regex_pattern(meta_data)

    # 3 Spezialfälle mit Text auseinandernehmen
    text_corpus = pp_special_text_split(meta_data, text_corpus)

    # 4 clean text corpus.
    text_corpus = clean(text_corpus)

    # 5 Find the beginning pattern in plenar file.
    find_beginnings = list(regex.finditer(begin_pattern, text_corpus))

    # If found more than once or none, handle depending on period.
    if len(find_beginnings) != 1:
        # continue
        return

    beginning_of_session = find_beginnings[0].span()[1]

    toc = text_corpus[:beginning_of_session]
    session_content = text_corpus[beginning_of_session:]

    # At this point the document has a unique beginning. The spoken
    # content begins after the matched phrase.

    # 6 ending
    # Append "END OF FILE" to document text, otherwise pattern is
    # not found, when appearing at the end of the file.
    session_content += "\n\nEND OF FILE"

    find_endings = list(regex.finditer(appendix_pattern, session_content))

    if len(find_endings) != 1:
        # continue
        return

    # Appendix begins before the matched phrase.
    end_of_session = find_endings[0].span()[0]

    appendix = session_content[end_of_session:]
    session_content = session_content[:end_of_session]

    # logger.debug("SC "+session_content[:100]+" ... "+session_content[-100:])

    save_path = RAW_TXT / folder_path.stem / input_file_path.stem
    save_path.mkdir(parents=True, exist_ok=True)

    # Save table of content, spoken content and appendix in separate files
    with open(save_path / "toc.txt", "w", encoding='utf-8') as text_file:
        text_file.write(toc)

    with open(save_path / "session_content.txt", "w", encoding='utf-8') as text_file:
        text_file.write(session_content)

    with open(save_path / "appendix.txt", "w", encoding='utf-8') as text_file:
        text_file.write(appendix)

    # Dictionary Comprehension to reduce meta_data
    keys_to_keep = ["document_number", "date"]
    meta_data_short = {k: meta_data[k] for k in keys_to_keep if k in meta_data}

    # other loglevel for dicttoxml!
    logging.getLogger('dicttoxml').setLevel(logging.WARNING)
    with open(save_path / "meta_data.xml", "wb") as result_file:
        result_file.write(dicttoxml.dicttoxml(meta_data_short))

    # TODO Was soll returned werden?

    return


def pp_split_xml_data(xml_file_path):
    """
    Opens a plenary protocol xml file and splits content into metadata and text corpus

    Args:
        xml_file_path (Path):

    Returns:
        meta_data (dict):
        text_corpus (str):
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
    if xml_file_path.stem != f"{int(meta_data["term"]):02d}{int(meta_data["document_number"].split("/")[1]):03d}":
        msg = f"meta_data / filepath not consistent: {str(xml_file_path)} {meta_data["document_number"]}"
        logger.debug(msg)

    return meta_data, text_corpus


def pp_define_regex_pattern(meta_data: dict):
    """
    Defines regex pattern for finding begin of speech_content respectively appendix of a plenar protocol.
    Based on a standard case, various exceptions from
    individual protocols (based on meta_data["document_number"]) are taken into account.

    Args:
        meta_data (dict):

    Returns:
        begin_pattern (compiled regex):
        appendix_pattern (compiled regex):

    """
    begin_pattern_electoral_term = r"Beginn?:?\s?(\d){1,2}(\s?[.,]\s?(\d){1,2})?\s?Uhr"
    appendix_pattern_electoral_term = r"\(Schlu(ß|ss)\s?:?(.*?)\d{1,2}\D+(\d{1,2})?(.*?)\)?|\(Ende der Sitzung: \d{1,2}\D+(\d{1,2}) Uhr\.?\)"

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
        appendix_pattern = r"Schluß: 12.06 Uhr\)\n\nDruck: Bonner Universitäts-Buchdruckerei, 53113 Bonn\n " + \
                           r"53003 Bonn, Telefon: 02 28/3 82 08 40, Telefax: 02 28/3 82 08 44\n\n20\n\nBun" + \
                           r"despräsident Dr. Roman Herzog\n\nDeutscher"
    elif meta_data["document_number"] == "14/21":
        appendix_pattern = r"\(Schluß: 22.18 Uhr\)\n\nAdelheid Tröscher\n\n1594"
    elif meta_data["document_number"] == "14/192":
        appendix_pattern = r"Vizepräsidentin Petra Bläss: Ich schließe die Aus-\nsprache\.(?=\n\nInter)"
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


def pp_special_text_split(meta_data: dict, text_corpus: str):
    """
    Change the content of text_corpus for some special cases (e.g. duplicated text corpus or two sessions in one protocol),
    dependent from meta_data["document_number"].
    In the standard case, text_corpus is returned unchanged.

    Args:
        meta_data (dict):
        text_corpus (str):

    Returns:
        text_corpus (str):

    """
    # Some files have issues which have to be handled manually
    # like a duplicated text corpus or two sessions in one file.
    if meta_data["document_number"] == "07/145":
        # In this file the whole text is duplicated.
        find_bundestag = list(
            regex.finditer("Deutscher Bundestag\n", text_corpus)
        )
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
            "(?<=\n)"
            + meta_data["document_number"][3:]
            + r"\. Sitzung(?=\nBonn)",
            text_corpus,
        )
        text_corpus = text_corpus[find_second.span()[0]:]

    return text_corpus
