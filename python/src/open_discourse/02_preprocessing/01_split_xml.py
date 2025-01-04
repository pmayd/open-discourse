"""
Iterate through xml files of session protocols,
either entire data or select electoral term and session.
This script processes only completed electoral terms with a full set of protocols
already downloaded in 01_download_raw_data. The last completed electoral term is
determined by the info in SESSIONS_PER_TERM.
"""

import logging
from pathlib import Path
from xml.etree.ElementTree import ParseError

import dicttoxml
import regex
from tqdm import tqdm

import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.definitions.other_definitions import SESSIONS_PER_TERM
from open_discourse.helper_functions.clean_text import clean
from open_discourse.helper_functions.logging_config import setup_and_get_logger
from open_discourse.helper_functions.session_file_iterator import session_file_iterator
from open_discourse.specific_functions.func_step02_func01 import (
    define_single_session_regex_pattern,
    single_session_special_text_split,
    split_single_session_xml_data,
)

logger = setup_and_get_logger(__file__, logging.DEBUG)
logger.info("Script 02_01 starts")

# input directory
RAW_XML = path_definitions.RAW_XML

# output directory
RAW_TXT = path_definitions.RAW_TXT
RAW_TXT.mkdir(parents=True, exist_ok=True)

# iterate through entire data or select term or session
# by default the iterator process form electoral term 3 until the last completed
# electoral term
max_term = max(SESSIONS_PER_TERM.keys())
while SESSIONS_PER_TERM[max_term] <= 0:
    max_term -= 1
    if max_term < 1:
        msg = ("No valid completed electoral term found. Check SESSIONS_PER_TERM.")
        raise ValueError(msg)
# change here for testuing with single terms or sessions
# for input_file_path in tqdm(session_file_iterator(RAW_XML,4, 19)):
for input_file_path in tqdm(session_file_iterator(RAW_XML, (3, max_term))):
    # ========================================
    # 1 split xml
    # ========================================
    try:
        meta_data, text_corpus = split_single_session_xml_data(input_file_path)
    except ParseError:
        continue  # logs are written in func
    # ========================================
    # 2 define regex patterns
    # ========================================
    begin_pattern, appendix_pattern = define_single_session_regex_pattern(meta_data)
    # ========================================
    # 3 special cases with text split
    # ========================================
    text_corpus = single_session_special_text_split(meta_data, text_corpus)
    # ========================================
    # 4 clean text corpus.
    # ========================================
    text_corpus = clean(text_corpus)
    # ========================================
    # 5 Find the beginning pattern in session protocol
    # ========================================
    find_beginnings = list(regex.finditer(begin_pattern, text_corpus))

    # If found more than once or none, handle depending on period.
    if len(find_beginnings) != 1:
        msg = (
            f"found {len(find_beginnings)} beginnings, 1 is expected in "
            f"{input_file_path.name}. No files written."
        )
        logging.warning(msg)
        continue

    beginning_of_session = find_beginnings[0].span()[1]

    toc = text_corpus[:beginning_of_session]
    session_content = text_corpus[beginning_of_session:]
    # At this point the document has a unique beginning. The spoken
    # content begins after the matched phrase.

    # ========================================
    # 6 Find the ending pattern in session protocol
    # ========================================
    # Append "END OF FILE" to document text, otherwise pattern is
    # not found, when appearing at the end of the file.
    session_content += "\n\nEND OF FILE"

    find_endings = list(regex.finditer(appendix_pattern, session_content))

    if len(find_endings) != 1:
        msg = (
            f"found {len(find_endings)} endings, 1 is expected in "
            f"{input_file_path.name}. No files written."
        )
        logging.warning(msg)
        continue

    # Appendix begins before the matched phrase.
    end_of_session = find_endings[0].span()[0]

    appendix = session_content[end_of_session:]
    session_content = session_content[:end_of_session]

    # ========================================
    # 7 write files
    # ========================================
    output_dir_path = RAW_TXT / input_file_path.parent.stem / input_file_path.stem
    output_dir_path.mkdir(parents=True, exist_ok=True)

    # Save table of content, spoken content and appendix in separate files
    with open(output_dir_path / "toc.txt", "w", encoding="utf-8") as text_file:
        text_file.write(toc)

    with open(
        output_dir_path / "session_content.txt", "w", encoding="utf-8"
    ) as text_file:
        text_file.write(session_content)

    with open(output_dir_path / "appendix.txt", "w", encoding="utf-8") as text_file:
        text_file.write(appendix)

    # Dictionary Comprehension to reduce meta_data
    keys_to_keep = ["document_number", "date"]
    meta_data_short = {k: meta_data[k] for k in keys_to_keep if k in meta_data}

    # other loglevel for dicttoxml!
    logging.getLogger("dicttoxml").setLevel(logging.WARNING)
    with open(output_dir_path / "meta_data.xml", "wb") as result_file:
        result_file.write(dicttoxml.dicttoxml(meta_data_short))

    # above writes successful?
    return_code = True
    for file_name in [
        "toc.txt",
        "session_content.txt",
        "appendix.txt",
        "meta_data.xml",
    ]:
        file_path = Path(output_dir_path / file_name)
        if not file_path.exists():
            msg = f"pp{input_file_path.stem}: File {file_name} not written."
            logging.error(msg)
            return_code = False


logger.info("Script 02_01 ends")
