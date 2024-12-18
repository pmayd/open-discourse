# Standardbibliotheken
import pytest
from collections import namedtuple

# Eigene Module
from open_discourse.specific_functions.functions_02_05 import convert_date_to_delta_seconds
from open_discourse.specific_functions.functions_02_05 import convert_electoral_term_dates
# ========================================
# test cases for convert_date_to_delta_seconds(TestElectionPeriod)
# ========================================
# definition of a named tuple for test case
TestElectionPeriod = namedtuple(
    "TestElectionPeriod", ["input", "expected", "exception"]
)
test_cases_convert_to_seconds = []
# 1) input ist kein string
# 2) inputstring ist im falschen dateformat
test_wrong_datatype = TestElectionPeriod((123,), expected=None, exception=TypeError)
test_wrong_dateformat = TestElectionPeriod(("30.12.1994",), expected=None, exception=ValueError)
test_cases_convert_to_seconds.append(test_wrong_dateformat)
test_cases_convert_to_seconds.append(test_wrong_datatype)

@pytest.mark.parametrize("case", test_cases_convert_to_seconds)
def test_convert_date_to_delta_seconds(case):

    if case.exception:
        with pytest.raises(case.exception):
            convert_date_to_delta_seconds(*case.input)
    else:
        assert case.expected == convert_date_to_delta_seconds(*case.input)

# ========================================
# test cases for convert_date_to_delta_seconds(TestElectionPeriod)
# ========================================
test_cases_convert_et_dates = [
    # Leere Liste
    TestElectionPeriod([], [], None),

    # Korrekte Eingabe
    TestElectionPeriod(
        [{"start_date": "1949-09-07", "end_date": "1953-10-05"}],
        [{"start_date": -641174400.0, "end_date": -512524800.0}],
        None,
    ),

    # Ungültiges Datum
    TestElectionPeriod(
        [{"start_date": "invalid-date", "end_date": "2004-12-31"}],
        [],
        None,  # Erwartet ein Log-Warning, kein Fehler
    ),

    # Teilweise korrekte Daten
    TestElectionPeriod(
        [
            {"start_date": "invalid-date", "end_date": "2004-12-31"},
            {"start_date": "1949-09-07", "end_date": "1953-10-05"},
        ],
        [{"start_date": -641174400.0, "end_date": -512524800.0}],
        None,
    ),
]


@pytest.mark.parametrize("case", test_cases_convert_et_dates)
def test_convert_electoral_term_dates(case):
    if case.exception:
        with pytest.raises(case.exception):
            convert_electoral_term_dates(case.input)
    else:
        result = convert_electoral_term_dates(case.input)
        assert result == case.expected

