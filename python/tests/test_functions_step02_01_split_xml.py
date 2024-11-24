import pytest
import tempfile
from collections import namedtuple
from pathlib import Path
import regex

import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.helper_functions.functions_step02_func_01_split_xml import pp_split_xml_data, pp_iterate_03_to_19, \
    pp_define_regex_pattern, pp_process_single_session
from xml.etree.ElementTree import ParseError

# DATA
RAW_XML = path_definitions.RAW_XML
RAW_TXT = path_definitions.RAW_TXT



# Definition Named Tuple for test cases
CaseDataforTest = namedtuple('CaseDataforTest', ['input', 'expected', 'exception'])

# ========================================
# test cases for pp_iterate_03_to_19 (list of namedtuple)
# ========================================
test_cases = []
test_cases.append(CaseDataforTest(input=(path_definitions.ROOT_DIR, RAW_TXT, -1), expected=None, exception=NotImplementedError))
test_cases.append(CaseDataforTest(input=(RAW_TXT, RAW_XML, -1), expected=None, exception=NotImplementedError))
test_cases.append(CaseDataforTest(input=(RAW_XML, RAW_TXT, -1), expected=None, exception=ValueError))
test_cases.append(CaseDataforTest(input=(RAW_XML, RAW_TXT, 1), expected=None, exception=ValueError))
test_cases.append(CaseDataforTest(input=(RAW_XML, RAW_TXT, 20), expected=None, exception=ValueError))
test_cases.append(CaseDataforTest((RAW_XML, RAW_TXT, 3, 333), expected=None, exception=ValueError))
test_cases.append(CaseDataforTest((RAW_XML, RAW_TXT, None, 333), expected=None, exception=ValueError))
test_cases.append(CaseDataforTest((RAW_XML, RAW_TXT, 4, 19), expected=None, exception=None))

@pytest.mark.parametrize("case", test_cases)
def test_pp_iterate_03_to_19(case):
    if case.exception:
        with pytest.raises(case.exception) as excinfo:
            pp_iterate_03_to_19(*case.input)
    else:
        result = pp_iterate_03_to_19(*case.input)
        assert result == case.expected



# ========================================
# test cases for pp_process_single_session (list of namedtuple)
# ========================================
test_cases = []

@pytest.mark.parametrize("case", test_cases)
def test_pp_process_single_session(case):
    input_path = Path(RAW_XML, "electoral_term_pp03.zip", "03004.xml")

    pp_process_single_session(input_path)
    # TODO Tests definieren
    assert False



# ========================================
# test cases for test_pp_get_xml_data (list of namedtuple)
# ========================================
test_cases = []
# TC0 PP03/004
filepath = Path(RAW_XML, "electoral_term_pp03.zip", "03004.xml")
metadata = {"term": "3", "document_type": "PLENARPROTOKOLL", "document_number": "03/4", "date": "05.11.1957"}
text = "text"
test_cases.append(CaseDataforTest(filepath, (metadata, text), None))

# TC1 PP04/019
filepath = Path(RAW_XML, "electoral_term_pp04.zip", "04019.xml")
metadata = {"term": "4", "document_type": "PLENARPROTOKOLL", "document_number": "04/19", "date": "14.03.1962"}
text = "text"
test_cases.append(CaseDataforTest(filepath, (metadata, text), None))

# TC2 PP18/039
filepath = Path(RAW_XML, "electoral_term_pp18.zip", "18039.xml")
metadata = {"term": "18", "document_type": "PLENARPROTOKOLL", "document_number": "18/39", "date": "05.06.2014"}
text = "text"
test_cases.append(CaseDataforTest(filepath, (metadata, text), None))

# TC3
filepath = Path(RAW_XML, "electoral_term_pp18.zip", "nonexistent.xml")
metadata = {}
text = ""
test_cases.append(CaseDataforTest(filepath, (metadata, text), FileNotFoundError))


@pytest.mark.parametrize("case", test_cases)
def test_pp_get_xml_data(case):
    if case.exception:
        with pytest.raises(case.exception) as excinfo:
            pp_split_xml_data(case.input)
        # if verbose:
        #     # Den Fehlertext auslesen
        #     error_msg = str(excinfo.value)
        #     # Den Fehlertext ausgeben
        #     print(f"\nRaised Exception: {case.exception.__name__}")
        #     print(f"Error message: {error_msg}")

    else:
        result = pp_split_xml_data(case.input)
        expected_metadata, expected_text = case.expected
        assert result[0] == expected_metadata
        if result[1] is not None:
            assert len(result[1]) > 10000
        else:
            assert result[1] is None



# ========================================
# test cases for test_pp_get_xml_data_mock (list of namedtuple)
# ========================================
test_cases = []
# Mock with invalid xml files, except the last one.
test_cases.append(CaseDataforTest("<root><invalid></root>", expected=None, exception=ParseError))
test_cases.append(CaseDataforTest("<root>", expected=None, exception=ParseError))
test_cases.append(CaseDataforTest("invalid content", expected=None, exception=ParseError))

# TC3
text = '''<DOKUMENT>
    <WAHLPERIODE>4</WAHLPERIODE>
    <DOKUMENTART>PLENARPROTOKOLL</DOKUMENTART>
    <DATUM>14.03.1962</DATUM>
    <TITEL>Plenarprotokoll vom 14.03.1962</TITEL>
    <TEXT>Deutscher Bundestag
    </TEXT>
    </DOKUMENT>'''                  #   Tag <NR> fehlt
test_cases.append(CaseDataforTest(text, expected=None, exception=AttributeError))

# TC4
metadata = {"term": "4", "document_type": "PLENARPROTOKOLL", "document_number": "04/19", "date": "14.03.1962"}
text = '''<DOKUMENT>
    <WAHLPERIODE>4</WAHLPERIODE>
    <DOKUMENTART>PLENARPROTOKOLL</DOKUMENTART>
    <NR>04/19</NR>
    <DATUM>14.03.1962</DATUM>
    <TITEL>Plenarprotokoll vom 14.03.1962</TITEL>
    <TEXT>Deutscher Bundestag
    </TEXT>
    </DOKUMENT>'''
test_cases.append(CaseDataforTest((metadata,text), expected=(metadata,"Deutscher Bundestag\n    "), exception=None))


@pytest.mark.parametrize("case", test_cases)
def test_pp_get_xml_data_mock(case):
    # Temporäre Datei mit xml-Inhalt erstellen
    if isinstance(case.input, str):
        xml_content = case.input
    else: xml_content = case.input[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as temp_file:
        temp_file.write(xml_content.encode('utf-8'))
        temp_file_path = Path(temp_file.name)

    # ========================================
    result = None
    try:
        result = pp_split_xml_data(temp_file_path)
        expected_metadata, expected_text = case.expected
        # assert result[0] == expected_metadata
        # if result[1] is not None:
        #     assert result[1] == expected_text
    except Exception as e:
        # Vergleiche den tatsächlichen Exception-Typ mit dem erwarteten, falls angegeben
        actual_exception = type(e).__name__

        if case.exception:
            # Erwartete Exception ist gesetzt, prüfe, ob sie übereinstimmt
            msg = f"Expected {case.exception.__name__}, but got {actual_exception}"
            assert actual_exception == case.exception.__name__, msg
        else:
            # unerwartete Exception
            msg = f"Unexpected exception raised: {str(e)}"
            assert actual_exception == None, msg

    finally:
        # Aufräumen der temporären Datei
        try:
            temp_file_path.unlink()  # Löschen der temporären Datei
        except OSError as e:
            print(f"Failed to delete temporary file {temp_file_path}: {e}")

    if result:
        assert result[0] == expected_metadata
        if result[1] is not None:
            assert result[1] == expected_text



# ========================================
# test cases for pp_define_regex_pattern (list of namedtuple)
# ========================================
test_cases = []

meta_data = {"document_number":"04/019"}
begin_pattern_default = regex.compile(r"Beginn?:?\s?(\d){1,2}(\s?[.,]\s?(\d){1,2})?\s?Uhr")
appendix_pattern_default = \
    regex.compile(r"\(Schlu(ß|ss)\s?:?(.*?)\d{1,2}\D+(\d{1,2})?(.*?)\)?|\(Ende der Sitzung: \d{1,2}\D+(\d{1,2}) Uhr\.?\)")
test_cases.append(CaseDataforTest(meta_data, expected=(begin_pattern_default, appendix_pattern_default), exception=None))

meta_data = {"document_number":"17/250"}
begin_pattern = regex.compile(r"Beginn: 9.02 Uhr(?=\nPräsident)")
appendix_pattern = regex.compile(r"\(Schluss: 0.52 Uhr\)\n\nIch")
test_cases.append(CaseDataforTest(meta_data, expected=(begin_pattern, appendix_pattern), exception=None))

@pytest.mark.parametrize("case", test_cases)
def test_pp_define_regex_pattern(case):
    if case.exception:
        with pytest.raises(case.exception) as excinfo:
            pp_define_regex_pattern(case.input)
    else:
        result = pp_define_regex_pattern(case.input)
        assert result == case.expected

