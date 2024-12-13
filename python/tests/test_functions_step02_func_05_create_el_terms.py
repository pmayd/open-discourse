import pytest
from collections import namedtuple
from open_discourse.specific_functions.functions_step02_func_05_create_el_terms import (
    convert_date_to_delta_seconds,
)

# definition of a named tuple for test case
TestElectionPeriod = namedtuple(
    "TestElectionPeriod", ["input", "expected", "exception"]
)

# ========================================
# test cases for convert_date_to_delta_seconds(TestElectionPeriod)
# ========================================
test_cases = []
test_wrong_datatype = TestElectionPeriod(123, expected=None, exception=ValueError)
test_cases.append(test_wrong_datatype)


@pytest.mark.parametrize("case", test_cases)
def test_convert_date_to_delta_seconds(case):
    # 1) input ist kein string
    # 2) inputstring ist im falschen dateformat
    if case.exception:
        with pytest.raises(case.exception):
            convert_date_to_delta_seconds(*case.input)
    else:
        assert case.expected == convert_date_to_delta_seconds(*case.input)
