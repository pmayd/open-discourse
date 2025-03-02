import logging
from pathlib import Path
from typing import Generator

from tqdm import tqdm

from open_discourse.definitions.other_definitions import SESSIONS_PER_TERM
from open_discourse.definitions.path_definitions import (
    CONTRIBUTIONS_EXTENDED_STAGE_01,
    CONTRIBUTIONS_EXTENDED_STAGE_02,
    CONTRIBUTIONS_EXTENDED_STAGE_03,
    CONTRIBUTIONS_EXTENDED_STAGE_04,
    RAW_TXT,
    RAW_XML,
    SPEECH_CONTENT_STAGE_01,
    SPEECH_CONTENT_STAGE_02,
    SPEECH_CONTENT_STAGE_03,
    SPEECH_CONTENT_STAGE_04,
)
from open_discourse.helper_functions.utils import get_term_from_path

# use predefined logger
logger = logging.getLogger()


def validate_term_session(
    param: int | tuple[int, int], max_value: int, param_name: str
):
    """
    Check for valid param. Conditions:
    type(param) == int and 0 < param <= max_value
    type(param) == tuple(int,int) and 0 < param[0] <= param[1] <= max_value

    Return range(int1,int2) of param with 0 < int1 <= int2 <= max_value

    Args:
        param (int | tuple[int,int]):   parameter to be checked
        max_value (int):                max_value for param
        param_name (str):               name of param (only used for error msg!)

    Returns: Range(int,int)

    """
    if not isinstance(max_value, int) or max_value < 1:
        msg = f"Invalid arg: max_value {max_value}."
        raise ValueError(msg)
    if param is not None:
        if isinstance(param, int):
            if not (1 <= param <= max_value):
                msg = f"Invalid arg: {param_name} {param} outside valid range."
                raise ValueError(msg)
            else:
                return list(range(param, param + 1))
        elif isinstance(param, tuple):
            if (
                len(param) != 2
                or not isinstance(param[0], int)
                or not isinstance(param[1], int)
            ):
                msg = f"Invalid arg: {param_name} {param} not a tuple[int,int]."
                raise ValueError(msg)
            elif not (
                (1 <= param[0] <= max_value)
                and (1 <= param[1] <= max_value)
                and (param[0] <= param[1])
            ):
                msg = (
                    f"Invalid arg: {param_name} {param} "
                    f"contains values outside valid range."
                )
                raise ValueError(msg)
            else:
                return list(range(param[0], param[1] + 1))
        else:
            msg = f"Invalid type {type(param)} for arg: {param_name} {param}."
            raise ValueError(msg)


def session_file_iterator(
    source_dir: Path,
    term: int | tuple[int, int] | None = None,
    session: int | tuple[int, int] | None = None,
) -> Generator[Path, None, None]:
    """
    Iterate through every subfolder of source_dir, e.g. RAW_XML from electoral term 01
    to the highest completed electoral term and return input_file_path.
    Call can be limited to one term or one session by additional args.
    Raises NotImplementedError resp. ValueError when args are not consistent or valid

    Args:
        source_dir (Path):  Path to input directory
        term (int):         electoral term
        session (int):      session number in electoral term

    Returns:
        Generator[Path, None, None]: input_file_path form Generator

    """

    # ==================================================================================
    # Check args
    # ==================================================================================
    pkl_path_list = (
        SPEECH_CONTENT_STAGE_01,
        SPEECH_CONTENT_STAGE_02,
        SPEECH_CONTENT_STAGE_03,
        SPEECH_CONTENT_STAGE_04,
        CONTRIBUTIONS_EXTENDED_STAGE_01,
        CONTRIBUTIONS_EXTENDED_STAGE_02,
        CONTRIBUTIONS_EXTENDED_STAGE_03,
        CONTRIBUTIONS_EXTENDED_STAGE_04,
    )

    if source_dir == RAW_XML:
        file_pattern = "*.xml"
    elif source_dir == RAW_TXT:
        file_pattern = "session_content.txt"
    elif source_dir in pkl_path_list:
        file_pattern = "*.pkl"
    else:
        raise NotImplementedError(f"Nothing implemented for {source_dir}.")
    assert source_dir.exists(), f"Input directory {source_dir} does not exist."

    # Don't process sub_directories outside scope of this function,
    # that is term 1 to the highest term in SESSIONS_PER_TERM or term in args
    max_term = max(SESSIONS_PER_TERM.keys())
    if term is None:
        term_list = list(range(1, max_term + 1))
    else:
        term_list = validate_term_session(term, max_term, "term")

    if session is not None:
        if not term or len(term_list) != 1:
            msg = (
                f"Invalid arg: exact one term must be set when session {session} is set"
            )
            raise ValueError(msg)
        else:
            max_session = SESSIONS_PER_TERM[term]
            session_list = validate_term_session(session, max_session, "session")
    # ==================================================================================
    # search for file_pattern
    # ==================================================================================
    tqdm_bar = None
    for term_number in term_list:
        total_per_term = (
            SESSIONS_PER_TERM[term_number] if not session else len(session_list)
        )
        # tqdm bar
        if tqdm_bar:
            tqdm_bar.close()

        tqdm_bar = tqdm(
            total=total_per_term,
            desc=f"Parsing term" f" {term_number:>2}...,",
            position=0,
        )

        if file_pattern == "*.xml":
            glob_pattern = f"electoral_term_pp{term_number:02}.zip/{file_pattern}"
        elif file_pattern == "session_content.txt":
            glob_pattern = f"electoral_term_pp{term_number:02}.zip/*/{file_pattern}"
        else:
            glob_pattern = f"electoral_term_pp{term_number:02}.zip/{file_pattern}"

        file_list = sorted(list(source_dir.glob(glob_pattern)), key=lambda x: x.name)
        for input_path in file_list:
            if not input_path.is_file():
                continue
            else:
                # session_content.txt-files are in a deeper directory
                if file_pattern == "session_content.txt":
                    check_term = int(input_path.parent.name[:2])
                    check_session = int(input_path.parent.name[2:])
                    check_dir = input_path.parent.parent
                else:
                    try:
                        check_term = int(input_path.stem[:2])
                        check_session = int(input_path.stem[2:])
                        check_dir = input_path.parent
                    except ValueError:
                        logging.warning(
                            f"Invalid file {input_path} should not exist "
                            f"in directoy!"
                        )
                        continue

                # Check for relevant session
                if session is not None:
                    if check_session not in session_list:
                        continue

                parent = input_path.parent
                # are there any sub_directories?
                if any(child.is_dir() for child in input_path.parent.iterdir()):
                    logging.warning(f"Path {parent} should not contain sub_dirs!")

                # check consistency in dir-name electoral_term
                term_in_path = get_term_from_path(str(check_dir))
                if term_in_path != check_term:
                    raise ValueError(f"inconsitent {input_path} {check_dir}")

                tqdm_bar.update(1)
                yield input_path

    if tqdm_bar:
        tqdm_bar.close()  # Schließt den letzten Fortschrittsbalken
