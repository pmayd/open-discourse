from collections import namedtuple
from pathlib import Path
from unittest.mock import patch

import pytest

from open_discourse.helper_functions.session_file_iterator import (
    session_file_iterator,
    validate_term_session,
)

# Definition Named Tuple for test cases, don't name ist Testcase!!!
CaseDataforTest = namedtuple("CaseDataforTest", ["input", "expected", "exception"])

# ======================================================================================
# test cases for test_validate_term_session()
# ======================================================================================
test_cases = []
test_cases.append(CaseDataforTest((5, 5, "single"), expected=[5], exception=None))
test_cases.append(
    CaseDataforTest((0, 4, "single"), expected=None, exception=ValueError)
)
test_cases.append(CaseDataforTest((5, 6, "single"), expected=[5], exception=None))
test_cases.append(
    CaseDataforTest((5, 4, "single"), expected=None, exception=ValueError)
)
test_cases.append(
    CaseDataforTest((5, -1, "single"), expected=None, exception=ValueError)
)
test_cases.append(
    CaseDataforTest(("5", 4, "single"), expected=None, exception=ValueError)
)
test_cases.append(
    CaseDataforTest((5, "5", "single"), expected=None, exception=ValueError)
)

test_cases.append(
    CaseDataforTest(((4, 5), 5, "double"), expected=[4, 5], exception=None)
)
test_cases.append(
    CaseDataforTest(((5, 4), 5, "double"), expected=None, exception=ValueError)
)
test_cases.append(
    CaseDataforTest(((3, 6), 5, "double"), expected=None, exception=ValueError)
)
test_cases.append(
    CaseDataforTest(((-1, 6), 7, "double"), expected=None, exception=ValueError)
)
test_cases.append(
    CaseDataforTest(((3.0, 6), 7, "double"), expected=None, exception=ValueError)
)


@pytest.mark.parametrize("case", test_cases)
def test_validate_term_session(case):
    if case.exception:
        with pytest.raises(case.exception):
            validate_term_session(*case.input)
    else:
        assert case.expected == validate_term_session(*case.input)


# ========================================
# test cases for session_file_iterator
# ========================================


test_cases = []
# test_cases.append(
#     CaseDataforTest(
#         {"source_dir": "anydir"},
#         expected=None,
#         exception=NotImplementedError,
#     )
# )
# test_cases.append(
#     CaseDataforTest(
#         {"source_dir": "SPEECH_CONTENT", "term": 4, "session": 19},
#         expected=None,
#         exception=NotImplementedError,
#     )
# )
test_cases.append(
    CaseDataforTest(
        {"source_dir": "RAW_XML", "term": 4, "session": 19},
        expected=["04019"],
        exception=None,
    )
)
test_cases.append(
    CaseDataforTest(
        {"source_dir": "RAW_XML", "term": 4, "session": None},
        expected=["04019", "04034", "04056"],
        exception=None,
    )
)
test_cases.append(
    CaseDataforTest(
        {"source_dir": "RAW_XML", "term": None, "session": None},
        expected=[
            "04019",
            "04034",
            "04056",
            "09019",
            "09034",
            "09056",
            "15019",
            "15034",
            "15056",
        ],
        exception=None,
    )
)
test_cases.append(
    CaseDataforTest(
        {"source_dir": "RAW_TXT", "term": 4, "session": 19},
        expected=["04019"],
        exception=None,
    )
)
test_cases.append(
    CaseDataforTest(
        {"source_dir": "RAW_TXT", "term": 4, "session": None},
        expected=["04019", "04034", "04056"],
        exception=None,
    )
)
test_cases.append(
    CaseDataforTest(
        {"source_dir": "RAW_TXT", "term": None, "session": None},
        expected=[
            "04019",
            "04034",
            "04056",
            "09019",
            "09034",
            "09056",
            "15019",
            "15034",
            "15056",
        ],
        exception=None,
    )
)

test_cases.append(
    CaseDataforTest(
        {"source_dir": "SPEECH_CONTENT_STAGE_02", "term": 4, "session": 19},
        expected=["04019"],
        exception=None,
    )
)
test_cases.append(
    CaseDataforTest(
        {"source_dir": "SPEECH_CONTENT_STAGE_02", "term": 4, "session": None},
        expected=["04019", "04034", "04056"],
        exception=None,
    )
)
test_cases.append(
    CaseDataforTest(
        {"source_dir": "SPEECH_CONTENT_STAGE_02", "term": None, "session": None},
        expected=[
            "04019",
            "04034",
            "04056",
            "09019",
            "09034",
            "09056",
            "15019",
            "15034",
            "15056",
        ],
        exception=None,
    )
)


@pytest.fixture()
def dynamic_patch_paths(tmp_path):
    # Patch die Definition von RAW_XML, um sie auf tmp_path zu setzen
    ###

    # DATA
    mocked_DATA = tmp_path / "data"
    mocked_DATA_RAW = mocked_DATA / "01_raw"
    mocked_DATA_CACHE = mocked_DATA / "02_cached"
    # mocked_DATA_FINAL = mocked_DATA / "03_final"

    # RAW
    mocked_RAW_XML = mocked_DATA_RAW / "xml"
    mocked_RAW_TXT = mocked_DATA_RAW / "txt"

    # SPEECH CONTENT
    mocked_SPEECH_CONTENT_STAGE_02 = mocked_DATA_CACHE / "speech_content" / "stage_02"

    # dict
    mocked_paths = {
        # "DATA_RAW": mocked_DATA_RAW,
        "RAW_XML": mocked_RAW_XML,
        "RAW_TXT": mocked_RAW_TXT,
        "SPEECH_CONTENT_STAGE_02": mocked_SPEECH_CONTENT_STAGE_02,
    }

    with patch.multiple(
        "open_discourse.helper_functions.session_file_iterator", **mocked_paths
    ):
        yield mocked_paths

    # with patch("open_discourse.helper_functions.session_file_iterator.RAW_XML",
    #     mocked_RAW_XML):
    #     yield mocked_RAW_XM


@pytest.fixture
@pytest.mark.parametrize("case", test_cases)
def prepare_valid_test_files(case, dynamic_patch_paths):
    """
    Prepare test files based on case
    """

    test_dir = dynamic_patch_paths[case.input["source_dir"]]
    if test_dir == dynamic_patch_paths["RAW_XML"]:
        suffix = ".xml"
    if test_dir == dynamic_patch_paths["RAW_TXT"]:
        suffix = ".txt"
    elif test_dir == dynamic_patch_paths["SPEECH_CONTENT_STAGE_02"]:
        suffix = ".pkl"
    # Get term and session from test case if available
    term = case.input["term"]
    if term is None:
        term = 4
    session = case.input["session"]
    if session is None:
        session = 19

    # testfiles in 3 directories, one is invalid filename format

    term_list = sorted([term, 9, 15])
    session_list = sorted([session, 34, 56])

    for t in term_list:

        if (
            test_dir == dynamic_patch_paths["RAW_XML"]
            or test_dir == dynamic_patch_paths["SPEECH_CONTENT_STAGE_02"]
        ):
            # create directories based on tmp_path
            create_dir = Path(test_dir, f"electoral_term_pp{t:02}.zip")
            create_dir.mkdir(parents=True, exist_ok=True)
            # invalid file
            sample_file = create_dir / f"x47P13{suffix}"
            sample_file.write_text("<content>Test</content>")
            for s in session_list:
                sample_file = create_dir / f"{t:02}{s:03}{suffix}"
                sample_file.write_text("<content>Test</content>")
        elif test_dir == dynamic_patch_paths["RAW_TXT"]:
            # create directories based on tmp_path
            create_dir = Path(test_dir, f"electoral_term_pp{t:02}.zip")
            create_dir.mkdir(parents=True, exist_ok=True)
            for s in session_list:
                create_dir = Path(
                    test_dir, f"electoral_term_pp{t:02}.zip", f"{t:02}{s:03}"
                )
                create_dir.mkdir(parents=True, exist_ok=True)
                sample_file = create_dir / "session_content.txt"
                sample_file.write_text("<content>Test</content>")


@pytest.mark.parametrize("case", test_cases)
def test_session_file_iterator(case, dynamic_patch_paths, prepare_valid_test_files):

    print("ZTT", dynamic_patch_paths[case.input["source_dir"]])
    # print(dynamic_patch_paths['DATA_RAW'])
    test_dir = dynamic_patch_paths[case.input["source_dir"]]
    assert "pytest" in str(test_dir)

    if case.exception:
        with pytest.raises(case.exception):
            next(session_file_iterator(*case.input))
    else:
        from types import GeneratorType

        print("TRE", test_dir)
        result = session_file_iterator(
            test_dir, case.input["term"], case.input["session"]
        )
        assert isinstance(result, GeneratorType)
        result_list = list(result)
        assert len(result_list) == len(case.expected)
        result_short_list = []
        for r in result_list:
            if "raw\\txt" in str(test_dir):
                print("BRT")
                assert r.stem == "session_content"
                result_short_list.append(r.parent.stem)
            else:
                result_short_list.append(r.stem)
        assert sorted(result_short_list) == sorted(case.expected)
        print("GRT", len(result_list))
        for g in result_list:
            print("KJU", g.stem)
