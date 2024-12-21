from collections import namedtuple
from pathlib import Path
from xml.etree.ElementTree import ParseError

import pytest
import regex
import pandas as pd

import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.specific_functions.functions_step02_func01 import (
    define_single_session_regex_pattern,
    ends_with_relative_path,
    iterate_preprocessing_completed_terms,
    process_single_session_protocol,
    split_single_session_xml_data,
)
from open_discourse.standalone_data_checks.functions_special_char import \
    count_special_chars

# Definition Named Tuple for test cases, don't name ist Testcase!!!
CaseDataforTest = namedtuple("CaseDataforTest", ["input", "expected", "exception"])

RAW_XML = path_definitions.RAW_XML
RAW_TXT = path_definitions.RAW_TXT

# ========================================
# test cases for test_count_special_chars
# ========================================
test_cases = []
data={"docnumber":["Test1"]}
test_cases.append(
    CaseDataforTest(
        ("Test1","ÜbelundGefährlich"), expected=pd.DataFrame(data), exception=None
    )
)
data={"docnumber":["Test2"],"&":[1],"&_matches":["Übel & Gefährlich###\n"]}
test_cases.append(
    CaseDataforTest(
        ("Test2","Übel & Gefährlich"), expected=pd.DataFrame(data),
            exception=None
    )
)
data={"docnumber":["Test3"],"&":[2],"&_matches":["es wird wieder Übel & Gefährlich & "
                                                 "mehr###\nr Übel & Gefährlich & "
                                                 "mehr###\n"]}
test_cases.append(
    CaseDataforTest(
        ("Test3","es wird wieder Übel & Gefährlich & mehr"), expected=pd.DataFrame(
            data),
            exception=None
    )
)


@pytest.mark.parametrize("case", test_cases)
def test_count_special_chars(case):
    if case.exception:
        with pytest.raises(case.exception):
            ends_with_relative_path(*case.input)
    else:
        assert case.expected.equals(count_special_chars(*case.input))
