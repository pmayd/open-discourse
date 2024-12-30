from collections import namedtuple

import pytest

from open_discourse.definitions.path_definitions import (
    RAW_TXT,
    RAW_XML,
    ROOT_DIR,
    SPEECH_CONTENT_STAGE_02,
)
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
test_cases.append(
    CaseDataforTest(
        "any_dir",
        expected=None,
        exception=NotImplementedError,
    )
)
test_cases.append(
    CaseDataforTest(
        {"source_dir": ROOT_DIR, "term": 4, "session": 19},
        expected=None,
        exception=NotImplementedError,
    )
)
test_cases.append(
    CaseDataforTest(
        (RAW_XML, 4, 19),
        expected=None,
        exception=None,
    )
)
test_cases.append(
    CaseDataforTest(
        (RAW_TXT, 4, 19),
        expected=None,
        exception=None,
    )
)
test_cases.append(
    CaseDataforTest(
        (SPEECH_CONTENT_STAGE_02, 4, 19),
        expected=None,
        exception=None,
    )
)
# test_cases.append(
#     CaseDataforTest(
#         {"source_dir": RAW_XML,  "term": 5, "session": -8},
#         expected=None,
#         exception=ValueError,
#     )
# )
# test_cases.append(
#     CaseDataforTest(
#         {"source_dir": RAW_XML,  "term": 5, "session": 0},
#         expected=None,
#         exception=ValueError,
#     )
# )
# test_cases.append(
#     CaseDataforTest(
#         {"source_dir": RAW_XML,  "term": 1},
#         expected=None,
#         exception=ValueError,
#     )
# )
#

@pytest.mark.parametrize("case", test_cases)
def test_session_file_iterator(case):
    # create directories based on tmp_path
    # source_dir = tmp_path / case.input["source_dir"].relative_to(
    #     ROOT_DIR
    # )  # only difference of pathes is used
    # source_dir.mkdir(parents=True, exist_ok=True)
    # target_dir = tmp_path / case.input["txt"].relative_to(ROOT_DIR)
    # target_dir.mkdir(parents=True, exist_ok=True)
    #
    # # Get term and session from test case if available
    # term = case.input.get("term", None)
    # session = case.input.get("session", None)
    #
    # # Change inside CaseDataforTest
    # case = case._replace(input=(source_dir, target_dir, term, session))

    if case.exception:
        with pytest.raises(case.exception):
            next(session_file_iterator(case.input))
    else:
        from types import GeneratorType

        result = session_file_iterator(*case.input)
        assert isinstance(result, GeneratorType)
        result_list = list(result)

        assert isinstance(result, GeneratorType)
        assert len(result_list) == len(case.expected)
        print("GRT", len(result_list))
        # for g in result:
        #     print(g)
