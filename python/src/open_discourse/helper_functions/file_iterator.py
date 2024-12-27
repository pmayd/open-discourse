import logging
from pathlib import Path

from tqdm import tqdm

from open_discourse.definitions.path_definitions import (
    RAW_XML,
    RAW_TXT,
    SPEECH_CONTENT_STAGE_01,
    SPEECH_CONTENT_STAGE_02,
    SPEECH_CONTENT_STAGE_03,
    SPEECH_CONTENT_STAGE_04,
    CONTRIBUTIONS_EXTENDED_STAGE_01,
    CONTRIBUTIONS_EXTENDED_STAGE_02,
    CONTRIBUTIONS_EXTENDED_STAGE_03,
    CONTRIBUTIONS_EXTENDED_STAGE_04,
)
from open_discourse.definitions.other_definitions import SESSIONS_PER_TERM
from open_discourse.helper_functions.utils import get_term_from_path
from open_discourse.specific_functions.func_step02_func01 import (
    ends_with_relative_path,
)


# use predefined logger
logger = logging.getLogger()


def file_iterator(
    source_dir: Path = RAW_XML,
    term: int | tuple[int, int] | None = None,
    session: int | tuple[int, int] | None = None,
):
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
        Path:               input_file_path

    """

    def validate_term_session(
        param: int | tuple[int, int], max_value: int, param_name: str
    ):
        # Don't process sub_directories outside scope of this function,
        # that is term 1 to the highest completed term or term in args
        if param is not None:
            if isinstance(param, int):
                if not (1 <= term <= max_value):
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
                    (1 <= param[0] <= max_value) and (1 <= param[1] <= max_value)
                ):
                    msg = f"Invalid arg: {param_name} {param} contains values outside valid range."
                    raise ValueError(msg)
                else:
                    return list(range(param[0], param[1] + 1))

    # ==================================================================================
    # Check args
    # ==================================================================================
    pck_path_list = (
        SPEECH_CONTENT_STAGE_01,
        SPEECH_CONTENT_STAGE_02,
        SPEECH_CONTENT_STAGE_03,
        SPEECH_CONTENT_STAGE_04,
        CONTRIBUTIONS_EXTENDED_STAGE_01,
        CONTRIBUTIONS_EXTENDED_STAGE_02,
        CONTRIBUTIONS_EXTENDED_STAGE_03,
        CONTRIBUTIONS_EXTENDED_STAGE_04,
    )

    if ends_with_relative_path(RAW_XML, source_dir):
        file_pattern = "*.xml"
    elif ends_with_relative_path(RAW_TXT, source_dir):
        file_pattern = "session_content.txt"
    elif any(ends_with_relative_path(path, source_dir) for path in pck_path_list):
        file_pattern = "*.pkl"
    else:
        raise NotImplementedError(f"Nothing implemented for {source_dir}.")
    assert source_dir.exists(), f"Input directory {source_dir} does not exist."

    # Don't process sub_directories outside scope of this function,
    # that is term 1 to the highest completed term or term in args

    max_term = max(SESSIONS_PER_TERM.keys())
    if term is None:
        term_list = list(range(1,max_term+1))
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
    pbar = tqdm(term_list)

    for elem in pbar: #, desc=f"Parsing term {elem:>2}..."):
        pbar.set_description(f"Parsing term {elem:>2}...")
        if file_pattern  == "*.xml":
            glob_pattern = f"electoral_term_pp{elem:02}.zip/{file_pattern}"
        elif file_pattern  == "session_content.txt":
            glob_pattern = f"electoral_term_pp{elem:02}/*/{file_pattern}"
        else:
            glob_pattern = f"electoral_term_pp{elem:02}/{file_pattern}"

        file_list = sorted(
            list(source_dir.glob(glob_pattern)), key=lambda x: x.name)
        for input_path in file_list:
            if not input_path.is_file():
                continue
            else:
                # session_content.txt-files are in a deeper directory
                if file_pattern =="session_content.txt":
                    check_term = int(input_path.parent.name[:2])
                    check_session = int(input_path.parent.name[2:])
                    check_dir = input_path.parent.parent
                else:
                    check_term = int(input_path.stem[:2])
                    check_session = int(input_path.stem[2:])
                    check_dir = input_path.parent

                # Check for relevant session
                if session is not None:
                    if check_session not in session_list:
                        continue

                parent = input_path.parent
                # Prüfen, ob das Verzeichnis der Datei keine weiteren Unterverzeichnisse hat
                if any(child.is_dir() for child in input_path.parent.iterdir()):
                    logging.warning(f"Path {parent} should not contain sub_dirs!")

                # check consistency in dir-name electoral_term
                term_in_path = get_term_from_path(check_dir)
                if term_in_path != check_term:
                    raise ValueError(f"inkonsitenz {input_path} {check_dir}")

                yield input_path


for elem in file_iterator(RAW_TXT,5):
    import pandas
    pass
    # print("CRA", elem)
