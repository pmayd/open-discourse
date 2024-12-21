import logging
from collections import Counter
from pathlib import Path
from xml.etree.ElementTree import ParseError

import pandas as pd
import regex
from tqdm import tqdm

import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.definitions.other_definitions import SESSIONS_PER_TERM
from open_discourse.helper_functions.utils import get_term_from_path
from open_discourse.specific_functions.functions_step02_func01 import (
    ends_with_relative_path,
    split_single_session_xml_data,
)
from open_discourse.standalone_data_checks.special_char_politicians import (
    get_politicians_with_special_chars,
)

RAW_XML = path_definitions.RAW_XML
VALID_CHARS = r"[a-zäöüßA-ZÄÖÜ0-9 ,;.:?!—/§%*\-\n\t\(\)\[\]„\"'–†½¼¾]"

# use predefined logger
logger = logging.getLogger()


def yield_xml_file_iterator(
    source_dir: Path = RAW_XML,
    term: int | None = None,
    session: int | None = None,
):
    """
    Iterate through every subfolder of source_dir, e.g. RAW_XML from electoral term 01
    to the highest completed electoral term, split xml-file and yield metadata and
    text_corpus
    Call can be limited to one term or one session by additional args.
    Raises NotImplementedError resp. ValueError when args are not consistent or valid

    Args:
        source_dir (Path):  Path to input directory
        term (int):         electoral term
        session (int):      session number in electoral term

    Returns:
        tuple(meta_data, text_corpus)
    """
    # ==================================================================================
    # Check args
    # ==================================================================================
    if ends_with_relative_path(RAW_XML, source_dir):
        input_suffix = ".xml"
    else:
        raise NotImplementedError("At the moment, only RAW_XML valid as source_dir")
    assert source_dir.exists(), f"Output directory {source_dir} does not exist."

    # Don't process sub_directories outside scope of this function,
    # that is term 1 to the highest completed term or term in args
    min_term = 1
    max_term = max(SESSIONS_PER_TERM.keys())

    if term is not None and not (min_term <= term <= max_term):
        msg = f"Invalid arg: term {term}"
        raise ValueError(msg)

    if session is not None:
        if not term:
            msg = f"Invalid arg: term must be set when session {session} is set"
            raise ValueError(msg)
        else:
            if not (1 <= session <= SESSIONS_PER_TERM[term]):
                msg = f"Invalid arg: session {session}"
                raise ValueError(msg)

    # ==================================================================================
    # Iterate through every input file acc. to input_suffix in every electoral term and
    # session, unless term and/or session are explicitly stated
    # ==================================================================================

    # Process every sub_directory of source_dir: electoral terms
    for folder_path in sorted(source_dir.iterdir()):
        if not folder_path.is_dir():
            continue
        term_number = get_term_from_path(str(folder_path))
        # ignore if no term number is found
        if term_number is None:
            logger.debug(f"No term number found in {folder_path.stem}.")
            continue
        # Don't process sub_directories outside scope of this function,
        # that is term 1 to the highest completed term or term in args
        if not (min_term <= term_number <= max_term) or (term and term != term_number):
            continue

        # Process all relevant files in sub_directory
        # if session from args, then only one input file
        if session is not None:
            input_files = list(
                Path(folder_path).glob(f"{term:02d}{session:03d}{input_suffix}")
            )
            logging.debug(folder_path)
            assert len(input_files) == 1, input_files
        # all sessions in sub_directory
        else:
            input_files = list(folder_path.glob("*" + input_suffix))
            msg = (
                f"number of sessions in {folder_path}: {len(input_files)}, "
                f"but should be {SESSIONS_PER_TERM[term_number]}"
            )
            assert len(input_files) == SESSIONS_PER_TERM[term_number], msg

        # Process every relevant file of folder_path: session
        for input_file_path in tqdm(
            input_files, desc=f"Parsing term {term_number:>2}..."
        ):
            # split xml
            try:
                meta_data, text_corpus = split_single_session_xml_data(input_file_path)
            except ParseError:
                msg = f"ParseError in: {input_file_path}"
                logging.warning(msg)
                continue
            yield (meta_data, text_corpus)


def special_char_apply_stopword(
    docnumber: str, text: str, special_char, frequency: int
):
    """
    #todo docstring
    """
    # Stopwort-Listen für jedes Zeichen
    stopword_dict = {
        "Å": ["Åland", "ÅÅÅ"],
        "à": [" à "],
        "ç": [" ça ", "façon", "rançais", "rançois"],
        "é": [
            "ttaché",
            "Café",
            "ommuniqué",
            "Conférenc",
            "Européenne",
            "Hué",
            "Tamblé",
        ],
        "è": ["Maizière", "èèè"],
        "ê": ["Arrêt", "ête "],
        "ë": ["Piëch", "Staël"],
        "û": ["coûte", "ûûû"],
        "Ł": ["Łódź", "Łužis"],
        "ź": ["Łódź", "źen"],
        "°": [
            "°/o",
        ],
        "'": ["ist's", "sei's"],
    }

    # add S

    # Łódź
    # if not isinstance(special_char,str):
    #     msg = f"{docnumber} {repr(special_char)} not str but " \
    #           f"{type(special_char)}; can't process"
    #     logging.warning(msg)
    #     return frequency, {repr(special_char) + "_matches": ""}

    # special_char = str(special_char)

    # if isinstance(special_char, bytes):  # Wenn es ein Byte-Muster ist
    #     # Byte-Muster in String umwandeln
    #     search_char = special_char.decode('utf-8', errors='ignore')  # Umwandlung von
    #     # Byte zu
    #     # String
    # else: search_char = special_char

    matches = list(regex.finditer(regex.escape(special_char), text))
    assert len(matches) == frequency

    relevant_matches = ""

    for match in matches:
        msg = f"{docnumber}: frequency for >>>{special_char}<<<: {frequency}"
        logging.debug(msg)

        flag_relevant_match = True
        if special_char in stopword_dict:
            for item in stopword_dict[special_char]:
                offset = item.index(special_char)
                if (
                    text[match.start() - offset : match.start() - offset + len(item)]
                    == item
                ):
                    flag_relevant_match = False
                    frequency -= 1
                    break

        # msg only if character is printable
        # and occurrence after application of stopwords
        if flag_relevant_match:
            match_context = text[max(match.start() - 20, 0) : match.start() + 20]
            relevant_matches = relevant_matches + match_context + "###\n"
            msg = (
                f"{docnumber} match found: '{match.group()}' at pos"
                f" {match.start()}: {match_context}"
            )
            logging.debug(msg)

    msg = f"{docnumber}: matches for {special_char}: {relevant_matches}"
    logging.debug(msg)

    return frequency, {special_char + "_matches": {relevant_matches}}


def count_special_chars(
    docnumber: str,
    text: str,
    valid_chars: str = (r"[a-zäöüßA-ZÄÖÜ0-9 ,;.:?!—/§%*\-\n\t\(\)\[\]„\"'–†½¼¾]"),
) -> pd.DataFrame | None:
    """
    # todo docstring
    Counts every special char in text and returns frequencies

    Args:
        docnumber (str):    docnumber
        text (str):         text
        valid_chars (str):  regex pattern for non-special chars
    """
    # All valid special chars are manually checked for election term 03-19
    # Explanation of some valid_chars:
    # '—' Geviertstrich Unicode Code Point: U+2014 UTF-8 Code: 0xE2 0x80 0x94
    # '-' Gedanken-/Bindestrich Unicode Code Point: U+2013 UTF-8 Code: 0xE2 0x80 0x93
    # '„' Deutsches öffnendes Anführungszeichen Unicode Code Point: U+201E
    #     UTF-8 Code: 0xE2 0x80 0x9E
    # '"' Doppeltes Anführungszeichen Unicode Code Point: U+0022 UTF-8 Code: 0x22
    # '†' Todeskreuz (Dagger) Unicode Code Point: U+2020 UTF-8 Kodierung: 0xE2 0x80 0xA0
    #
    # Correction needed for
    # Œ

    # TODO # \t hier zugelassen, muss aber später aus text-corpus entfernt werden!

    # negative pattern: find chars which are not allowed
    regpat_invalid = f"[^{valid_chars[1:-1]}]"

    # find all invalid chars
    invalid_chars = regex.findall(regpat_invalid, text)

    # count frequency of invali chars
    frequencies = Counter(invalid_chars)
    # frequencies = Counter(dict(sorted(frequencies.items())))  # todo Braucht das wer ?
    # später wird der df sortiert

    # check for stopwords
    relevant_matches = {}
    for key, count in list(frequencies.items()):
        frequencies[key], relevant_match = special_char_apply_stopword(
            docnumber, text, key, frequencies[key]
        )
        msg = (
            f"relevant matches for {str(key)} {type(relevant_match)}"
            f" {len(relevant_match)} {relevant_match}"
        )

        logging.debug(msg)
        relevant_matches |= relevant_match  # append to dict

    # # delete zero entries
    # for key, count in list(frequencies.items()):  # use derivate of frequencies to
    #     # change in frequencies
    #     if frequencies[key] == 0:
    #         frequencies.pop(key)
    #     elif frequencies[key] < 0:
    #         msg = f"frequency < 0 should not occur: {key}:{frequencies[key]}"
    #         raise ValueError(msg)

    if frequencies:
        msg = f"{docnumber} frequency of invalid chars: {frequencies}"
        logger.debug(msg)
    # else:
    #     msg = f"{docnumber} no invalid chars found"
    #     logger.debug(msg)
    #     return None

    # --------------------
    # Only when frequencies are filled!
    # --------------------
    # create df from Counter
    df = pd.DataFrame([frequencies])
    df["docnumber"] = docnumber
    # docnumber as 1st column
    df = df[["docnumber"] + [col for col in df.columns if col != "docnumber"]]
    assert len(df) == 1, f"xx df len:{len(df)}; should be 1"
    df_matches = pd.DataFrame.from_dict(relevant_matches, orient="index").T
    assert len(df_matches) in (0, 1), f"df len:{len(df_matches)}; should be 0 or 1"

    # concat frequencies and matches
    df = pd.concat([df.fillna(0), df_matches], axis=1)
    assert len(df) == 1, f"df final  len:{len(df_matches)}; zz should be 1"

    logging.debug(f"df.shape {df.shape}")

    return df


# result = count_special_chars("Testdummy","Übel & Gefährlich")
# #data={"docnumber":["Testdummy"],"&":[1],"&_matches":["Übel & Gefährlich"]}
# print("KJS",result.info(),result)


def check_special_pairs(docnumber, frequencies, text):
    """
    #todo docstring
    Args:
        docnumber ():
        frequencies ():
        text ():

    """

    open_chars = "([{„"
    close_chars = ")]}“"
    need_escape_char = "([{)]}"
    assert len(open_chars) == len(close_chars)

    result = []
    return_result = []
    # Iterate through matching pairs
    for open_c, close_c in zip(open_chars, close_chars):
        open_c_reg = open_c
        if open_c in need_escape_char:
            open_c_reg = "\\" + open_c
        close_c_reg = close_c
        if close_c in need_escape_char:
            close_c_reg = "\\" + close_c
        tmp_text = text
        # both parts of pair exists
        if open_c in frequencies and close_c in frequencies:
            msg = f"{docnumber}: pair frequencies '{open_c}':{frequencies[open_c]} / '{close_c}':{frequencies[close_c]}"
            logging.debug(msg)

            regpat = rf"{open_c_reg}[^{open_c_reg}{close_c_reg}]+{close_c_reg}"
            result = regex.findall(regpat, tmp_text, flags=regex.DOTALL)
            msg = f"{docnumber}: {len(result)} '{open_c}{close_c}' pairs found out of {frequencies[open_c]} / {frequencies[close_c]}"
            logging.debug(msg)
        # Pair doesn't exist
        elif open_c not in frequencies and close_c not in frequencies:
            msg = f"{docnumber}: No '{open_c}{close_c}' pairs found"
            logging.debug(msg)
            continue  # Goto next pair
        # one part of pair exists
        # else:
        #     msg = f"JKL >>>{open_c}<<< >>>{close_c}<<<"
        #     logging.debug(msg)
        #     regquant25 = r"{25}?"
        #     regpat = rf".{regquant25}({open_c_reg}|{close_c_reg}).{regquant25}"
        #     result = regex.findall(regpat, tmp_text, flags=regex.DOTALL)
        #     msg = f"{docnumber}: {len(result)} mismatched parts of {open_c}{close_c} pairs found out of {frequencies[open_c]} / {frequencies[close_c]}"
        #     logging.debug(msg)

        if len(result) == frequencies[open_c] == frequencies[close_c]:
            msg = f"{docnumber}: all '{open_c}{close_c}' occurences in pairs"
            logging.debug(msg)
        else:
            for result_part in result:
                tmp_text = tmp_text.replace(
                    result_part, ""
                )  # Ersetze jedes Segment durch einen leeren String

            regquant25 = r"{25}?"
            # regpat = rf".{regquant25}({open_c_reg}|{close_c_reg}).{regquant25}"
            regpat = rf".{regquant25}[{open_c_reg}{close_c_reg}].{regquant25}"
            regpat = rf".{regquant25}[{open_c}{close_c}].{regquant25}"
            msg = f"the new regpat: {regpat}"
            logging.debug(msg)

            result_redux = regex.findall(regpat, tmp_text, flags=regex.DOTALL)
            return_result.append(result_redux)

            msg = f"RTT {len(text)} {len(tmp_text)} {result_redux}"
            logging.debug(msg)

            msg = (
                f"{docnumber}: {len(result_redux)} unmatched occurences for '"
                f"{open_c}{close_c}' pairs"
            )
            logging.debug(msg)

    logging.debug(f"ENDE {len(return_result)} {return_result}")
    return return_result


def special_cases(docnumber, frequencies):
    """
    Hier werden spezifishce Sonderzeichen protokollweise erlaubt,
    z.B: wg. frendsprachlicher Zitate oder NAmern

    """

    if docnumber == "05/24":
        frequencies.subtract("Ż")  # equivalent to -= 1

    elif docnumber == "08/42":
        for char in set("ιςλπνόγδοε"):
            frequencies.subtract(char)

    return frequencies


def get_stopword_dict() -> dict:
    """
    Return a list of stopwords where special chars are allowed

    Returns:
        dict: dict of stopwords
    """

    def add_list_to_dict(word_list):
        # check every entry in list
        for e in word_list:
            for m in regpat.finditer(e):
                c = m.group()
                # key exists already
                if c in stopword_dict:
                    # but value is new
                    if e not in stopword_dict[c]:
                        stopword_dict[c].append(e)
                else:
                    # key doesn't exist, entry has to be a list!
                    stopword_dict[c] = [e]

    # create stopword_dict for every relevant special char
    stopword_dict = {}
    # ==================================================================================
    # Define stopwords and add to stopword_dict
    # It's possible that one stopword creates more than one entry in dict, e.g. Łódź
    # ==================================================================================
    stopword_list = [
        "Åland",
        " à ",
        " ça ",
        "façon",
        "rançais",
        "rançois",
        "Łódź",
        "Łužis",
        "źen",
        "ttaché",
        "Café",
        "ommuniqué",
        "Conférenc",
        "Européenne",
        "Hué",
        "Tamblé",
        "Maizière",
        "Arrêt",
        "ête ",
        "Piëch",
        "Staël",
        "coûte",
        "°/o",
        "ist's",
        "sei's",
    ]

    valid_name_chars = r"[a-zäöüßA-ZÄÖÜ -.]"
    # compile regex pattern to find chars that are NOT in VALID_CHARS
    regpat = regex.compile(f"[^{valid_name_chars[1:-1]}]")

    add_list_to_dict(stopword_list)

    # ==================================================================================
    # Add politician names with special chars to stopword_dict
    # ==================================================================================
    # These chars are 'normal' chars in german names
    valid_name_chars = r"[a-zäöüßA-ZÄÖÜ -.]"
    # compile regex pattern to find chars that are NOT in VALID_CHARS
    regpat = regex.compile(f"[^{valid_name_chars[1:-1]}]")

    politicians_list = get_politicians_with_special_chars()
    add_list_to_dict(politicians_list)

    return stopword_dict


# print(get_stopword_dict())
