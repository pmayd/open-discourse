from collections import namedtuple
from pathlib import Path
from xml.etree.ElementTree import ParseError

import pytest
import regex

import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.specific_functions.functions_step02_func01 import (
    define_single_session_regex_pattern,
    ends_with_relative_path,
    iterate_preprocessing_completed_terms,
    process_single_session_protocol,
    split_single_session_xml_data,
)

# Definition Named Tuple for test cases, don't name ist Testcase!!!
CaseDataforTest = namedtuple("CaseDataforTest", ["input", "expected", "exception"])

RAW_XML = path_definitions.RAW_XML
RAW_TXT = path_definitions.RAW_TXT

# ========================================
# test cases for ends_with_relative_path (list of namedtuple)
# ========================================
test_cases = []
test_cases.append(CaseDataforTest((RAW_XML, RAW_XML), expected=True, exception=None))
test_cases.append(CaseDataforTest((RAW_XML, RAW_TXT), expected=False, exception=None))
test_cases.append(
    CaseDataforTest(
        (Path("/data/data"), Path("text/data")), expected=None, exception=ValueError
    )
)


@pytest.mark.parametrize("case", test_cases)
def test_ends_with_relative_path(case):
    if case.exception:
        with pytest.raises(case.exception):
            ends_with_relative_path(*case.input)
    else:
        assert case.expected == ends_with_relative_path(*case.input)


# ========================================
# test cases for iterate_preprocessing_completed_terms (list of namedtuple)
# ========================================
test_cases = []
test_cases.append(
    CaseDataforTest(
        {"xml": path_definitions.ROOT_DIR, "txt": RAW_TXT, "term": -1},
        expected=None,
        exception=NotImplementedError,
    )
)
test_cases.append(
    CaseDataforTest(
        {"xml": RAW_TXT, "txt": RAW_XML, "term": 1},
        expected=None,
        exception=NotImplementedError,
    )
)
test_cases.append(
    CaseDataforTest(
        {"xml": RAW_XML, "txt": RAW_TXT, "term": 0}, expected=None, exception=ValueError
    )
)
test_cases.append(
    CaseDataforTest(
        {"xml": RAW_XML, "txt": RAW_TXT, "term": 0, "session": 0},
        expected=None,
        exception=ValueError,
    )
)
test_cases.append(
    CaseDataforTest(
        {"xml": RAW_XML, "txt": RAW_TXT, "term": -1},
        expected=None,
        exception=ValueError,
    )
)
test_cases.append(
    CaseDataforTest(
        {"xml": RAW_XML, "txt": RAW_TXT, "term": 5, "session": -8},
        expected=None,
        exception=ValueError,
    )
)
test_cases.append(
    CaseDataforTest(
        {"xml": RAW_XML, "txt": RAW_TXT, "term": 5, "session": 0},
        expected=None,
        exception=ValueError,
    )
)
test_cases.append(
    CaseDataforTest(
        {"xml": RAW_XML, "txt": RAW_TXT, "term": 1}, expected=None, exception=ValueError
    )
)
test_cases.append(
    CaseDataforTest(
        {"xml": RAW_XML, "txt": RAW_TXT, "term": 20, "session": 7},
        expected=None,
        exception=ValueError,
    )
)
test_cases.append(
    CaseDataforTest(
        {"xml": RAW_XML, "txt": RAW_TXT, "term": 3, "session": 333},
        expected=None,
        exception=ValueError,
    )
)
test_cases.append(
    CaseDataforTest(
        {"xml": RAW_XML, "txt": RAW_TXT, "session": 17},
        expected=None,
        exception=ValueError,
    )
)
test_cases.append(
    CaseDataforTest(
        {"xml": RAW_XML, "txt": RAW_TXT, "term": 4, "session": 19},
        expected=None,
        exception=None,
    )
)


@pytest.mark.parametrize("case", test_cases)
def test_pp_iterate_03_to_19(tmp_path, case):
    # create directories based on tmp_path
    source_dir = tmp_path / case.input["xml"].relative_to(
        path_definitions.ROOT_DIR
    )  # only difference of pathes is used
    source_dir.mkdir(parents=True, exist_ok=True)
    target_dir = tmp_path / case.input["txt"].relative_to(path_definitions.ROOT_DIR)
    target_dir.mkdir(parents=True, exist_ok=True)

    # Get term and session from test case if available
    term = case.input.get("term", None)
    session = case.input.get("session", None)

    # Change inside CaseDataforTest
    case = case._replace(input=(source_dir, target_dir, term, session))

    if case.exception:
        with pytest.raises(case.exception):
            iterate_preprocessing_completed_terms(*case.input)
    else:
        result = iterate_preprocessing_completed_terms(*case.input)
        assert result == case.expected


# ========================================
# test cases for process_single_session_protocol (list of namedtuple)
# ========================================
test_cases = []
xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE DOKUMENT SYSTEM "BUNDESTAGSDOKUMENTE.dtd">
<DOKUMENT>
  <WAHLPERIODE>4</WAHLPERIODE>
  <DOKUMENTART>PLENARPROTOKOLL</DOKUMENTART>
  <NR>04/19</NR>
  <DATUM>14.03.1962</DATUM>
  <TITEL>Plenarprotokoll vom 14.03.1962</TITEL>
  <TEXT>Deutscher Bundestag
19. Sitzung
Bonn, den 14. März 1962
Inhalt:
Fragestunde (Drucksache IV/239) Frage des Abg. Lohmar:
Sondermarken zum 20. Jahrestag des 20. Juli 1944
Dr. Steinmetz, Staatssekretär . . . 625 B Frage des Abg. Rademacher:
Münzfernsprecher auf Bahnsteigen der Bundesbahn
Nächste Sitzung  	695 D
Anlage 	 697
Deutscher Bundestag — 4. Wahlperiode — 19. Sitzung. Bonn, Mittwoch, den 14. März
1962	625
19. Sitzung
Bonn, den 14. März 1962
Stenographischer Bericht
Beginn: 9.03 Uhr.
Präsident D. Dr. Gerstenmaier: Die Sitzung ist eröffnet.
Ich rufe auf Punkt 1 der Tagesordnung: Fragestunde (Drucksache IV/239).
Ich berufe die nächste Sitzung auf Donnerstag, den 15. März 1962, 9 Uhr.
Die Sitzung ist geschlossen.
(Schluß der Sitzung: 19.06 Uhr.)

Liste der beurlaubten Abgeordneten
Abgeordnete(r)	beurlaubt bis einschließlich
a) Beurlaubungen
Arendt (Wattenscheid)	15.  3.
b) Urlaubsanträge
Schlick	14. 4.</TEXT>
</DOKUMENT>
"""
filename = "04019.xml"
test_cases.append(CaseDataforTest((filename, xml), expected=4, exception=None))


@pytest.mark.parametrize("case", test_cases)
def test_pp_process_single_session(tmp_path, case):
    (tmp_path / "xml").mkdir(parents=True, exist_ok=True)
    temp_file_1 = Path(tmp_path, "xml", case.input[0])
    temp_file_1.write_text(case.input[1], encoding="utf-8")

    process_single_session_protocol(temp_file_1, (tmp_path / "txt"))

    ###
    # expected path and files
    expected_path = Path(tmp_path, "txt")
    expected_files = ["toc.txt", "session_content.txt", "appendix.txt", "meta_data.xml"]

    # check if the number of written files is as expected
    created_files = list(expected_path.iterdir())
    msg = f" {len(created_files)} files written from {case.expected}"
    assert len(created_files) == case.expected, msg

    # Überprüfen Sie, ob alle erwarteten Dateien existieren
    for filename in expected_files:
        file_path = expected_path / filename
        assert file_path.is_file(), f"Die Datei {filename} wurde nicht erstellt"

    ###


# ========================================
# test cases for test_pp_split_xml_data (list of namedtuple)
# ========================================
test_cases = []

test_cases.append(
    CaseDataforTest(
        ("Testdummy1.xml", "<root><invalid></root>"),
        expected=None,
        exception=ParseError,
    )
)
test_cases.append(
    CaseDataforTest(("Testdummy2.xml", "<root>"), expected=None, exception=ParseError)
)
test_cases.append(
    CaseDataforTest(
        ("Testdummy3.xml", "invalid content"), expected=None, exception=ParseError
    )
)
test_cases.append(
    CaseDataforTest(
        ("Testdummy3.doc", "invalid content"),
        expected=None,
        exception=FileNotFoundError,
    )
)

# ----------
# Tests with same metadate
expected_metadata = {
    "term": "3",
    "document_type": "PLENARPROTOKOLL",
    "document_number": "03/4",
    "date": "05.11.1957",
}

xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE DOKUMENT SYSTEM "BUNDESTAGSDOKUMENTE.dtd">
<DOKUMENT>
  <WAHLPERIODE>3</WAHLPERIODE>
  <DOKUMENTART>PLENARPROTOKOLL</DOKUMENTART>
  <NR>03/4</NR>
  <DATUM>05.11.1957</DATUM>
  <TITEL>Plenarprotokoll vom 05.11.1957</TITEL>
  <TEXT>Deutscher Bundestag — 3. Wahlperiode — 4. Sitzung. Bonn, Dienstag,
den 5. November 1957
4. Sitzung
Bonn, den 5. November 1957
Inhalt:
Die Sitzung ist geschlossen.
(Schluß: 17.53 Uhr.)
Fürst von Bismarck	20. 12.
Kühlthau	25. 11.
Scheel	15. 12.</TEXT>
</DOKUMENT>
"""
text = """Deutscher Bundestag — 3. Wahlperiode — 4. Sitzung. Bonn, Dienstag,
den 5. November 1957
4. Sitzung
Bonn, den 5. November 1957
Inhalt:
Die Sitzung ist geschlossen.
(Schluß: 17.53 Uhr.)
Fürst von Bismarck	20. 12.
Kühlthau	25. 11.
Scheel	15. 12."""
test_cases.append(CaseDataforTest(("03004.xml", xml), (expected_metadata, text), None))
test_cases.append(CaseDataforTest(("03005.xml", xml), (expected_metadata, text), None))
# Filename inconsistent to tag NR

xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE DOKUMENT SYSTEM "BUNDESTAGSDOKUMENTE.dtd">
<DOKUMENT>
  <WAHLPERIODE>3</WAHLPERIODE>
  <DOKUMENTART>PLENARPROTOKOLL</DOKUMENTART>
    <DATUM>05.11.1957</DATUM>
  <TITEL>Plenarprotokoll vom 05.11.1957</TITEL>
  <TEXT>Deutscher Bundestag — 3. Wahlperiode — 4. Sitzung. Bonn, Dienstag,
  den 5. November 1957
4. Sitzung
Bonn, den 5. November 1957
Inhalt:
Die Sitzung ist geschlossen.
(Schluß: 17.53 Uhr.)
Fürst von Bismarck	20. 12.
Kühlthau	25. 11.
Scheel	15. 12.</TEXT>
</DOKUMENT>
"""
test_cases.append(
    CaseDataforTest(("03004.xml", xml), (expected_metadata, text), AttributeError)
)  # Tag <NR> fehlt

xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE DOKUMENT SYSTEM "BUNDESTAGSDOKUMENTE.dtd">
<DOKUMENT>
  <WAHLPERIODE>3</WAHLPERIODE>
  <DOKUMENTART>PLENARPROTOKOLL</DOKUMENTART>
  <NR>03/4</NR>
  <DATUM>05.11.1957</DATUM>
  <TITEL>Plenarprotokoll vom 05.11.1957</TITEL>
  TEXT>Deutscher Bundestag — 3. Wahlperiode — 4. Sitzung. Bonn, Dienstag,
  den 5. November 1957
4. Sitzung
Bonn, den 5. November 1957
Inhalt:
Die Sitzung ist geschlossen.
(Schluß: 17.53 Uhr.)
Fürst von Bismarck	20. 12.
Kühlthau	25. 11.
Scheel	15. 12.</TEXT>
</DOKUMENT>
"""
test_cases.append(
    CaseDataforTest(("03004.xml", xml), (expected_metadata, text), ParseError)
)  # Fehlerhafter Tag TEXT
# ----------

# TC4
expected_metadata = {
    "term": "4",
    "document_type": "PLENARPROTOKOLL",
    "document_number": "04/19",
    "date": "14.03.1962",
}
xml = """<DOKUMENT>
    <WAHLPERIODE>4</WAHLPERIODE>
    <DOKUMENTART>PLENARPROTOKOLL</DOKUMENTART>
    <NR>04/19</NR>
    <DATUM>14.03.1962</DATUM>
    <TITEL>Plenarprotokoll vom 14.03.1962</TITEL>
    <TEXT>Deutscher Bundestag
    </TEXT>
    </DOKUMENT>"""
test_cases.append(
    CaseDataforTest(
        ("04019.xml", xml),
        expected=(expected_metadata, "Deutscher Bundestag\n    "),
        exception=None,
    )
)


@pytest.mark.parametrize("case", test_cases)
def test_pp_split_xml_data(tmp_path, case):
    # create temp_files for test
    temp_file_1 = tmp_path / case.input[0]
    temp_file_1.write_text(case.input[1], encoding="utf-8")

    if case.exception:
        with pytest.raises(case.exception):
            split_single_session_xml_data(temp_file_1)
    else:
        result = split_single_session_xml_data(temp_file_1)
        assert result[0] == case.expected[0]
        assert result[1] == case.expected[1]


# ========================================
# test cases for define_single_session_regex_pattern (list of namedtuple)
# ========================================
test_cases = []

meta_data = {"document_number": "04/019"}
begin_pattern_default = regex.compile(
    r"Beginn?:?\s?(\d){1,2}(\s?[.,]\s?(\d){1,2})?\s?Uhr"
)
appendix_pattern_default = regex.compile(
    r"\(Schlu(ß|ss)\s?:?(.*?)\d{1,2}\D+(\d{1,2})?(.*?)\)?|\(Ende der Sitzung: \d{"
    r"1,2}\D+(\d{1,2}) Uhr\.?\)"
)
test_cases.append(
    CaseDataforTest(
        meta_data,
        expected=(begin_pattern_default, appendix_pattern_default),
        exception=None,
    )
)

meta_data = {"document_number": "17/250"}
begin_pattern = regex.compile(r"Beginn: 9.02 Uhr(?=\nPräsident)")
appendix_pattern = regex.compile(r"\(Schluss: 0.52 Uhr\)\n\nIch")
test_cases.append(
    CaseDataforTest(
        meta_data,
        expected=(begin_pattern, appendix_pattern),
        exception=None,
    )
)


@pytest.mark.parametrize("case", test_cases)
def test_pp_define_regex_pattern(case):
    if case.exception:
        with pytest.raises(case.exception):
            define_single_session_regex_pattern(case.input)
    else:
        result = define_single_session_regex_pattern(case.input)
        assert result == case.expected
