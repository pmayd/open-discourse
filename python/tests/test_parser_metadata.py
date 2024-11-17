import pytest
import re
from xml.etree.ElementTree import ElementTree, fromstring
from open_discourse.helper_functions.parser import get_doc_metadata, Metadata


# Sample XML content based on the provided example
SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE DOKUMENT SYSTEM "BUNDESTAGSDOKUMENTE.dtd">
<DOKUMENT>
  <WAHLPERIODE>1</WAHLPERIODE>
  <DOKUMENTART>PLENARPROTOKOLL</DOKUMENTART>
  <NR>01/1</NR>
  <DATUM>07.09.1949</DATUM>
  <TITEL>Plenarprotokoll vom 07.09.1949</TITEL>
  <TEXT>Deutscher Bundestag — 1. Sitzung. Bonn, Mittwoch, den 7. September 1949	1
1. Sitzung.
Bonn, Mittwoch, den 7. September 1949.
(Schluß der Sitzung: 18 Uhr 18 Minuten )</TEXT>
</DOKUMENT>"""

# Function to validate the date format (DD.MM.YYYY)
DATE_REGEX = r"^\d{2}\.\d{2}\.\d{4}$"

def test_get_doc_metadata_valid():
    # Arrange: Parse the sample XML into an ElementTree
    tree = ElementTree(fromstring(SAMPLE_XML))

    # Act: Call the function
    metadata = get_doc_metadata(tree)

    # Assert: Verify the extracted metadata
    assert metadata.document_number == "01/1"
    assert metadata.date == "07.09.1949"
    # Assert: Verify the date format (DD.MM.YYYY)
    assert re.match(DATE_REGEX, metadata.date)


def test_get_doc_metadata_missing_elements():
    # Arrange: Create XML with missing NR and DATUM
    invalid_xml = """<DOKUMENT>
                        <WAHLPERIODE>1</WAHLPERIODE>
                        <DOKUMENTART>PLENARPROTOKOLL</DOKUMENTART>
                     </DOKUMENT>"""
    tree = ElementTree(fromstring(invalid_xml))

    # Act & Assert: Ensure AttributeError is raised for missing elements
    with pytest.raises(AttributeError):
        get_doc_metadata(tree)


def test_get_doc_metadata_empty_elements():
    # Arrange: Create XML with empty NR and DATUM
    empty_elements_xml = """<DOKUMENT>
                                <NR></NR>
                                <DATUM></DATUM>
                             </DOKUMENT>"""
    tree = ElementTree(fromstring(empty_elements_xml))

    # Act: Call the function
    metadata = get_doc_metadata(tree)

    # Assert: Verify the metadata contains empty strings and raise a custom error if they are empty
    assert metadata.document_number == "", f"Expected empty document number, got: '{metadata.document_number}'"
    assert metadata.date == "", f"Expected empty date, got: '{metadata.date}'"
    if not metadata.document_number:
        raise ValueError("Empty string found for document number.")
    if not metadata.date:
        raise ValueError("Empty string found for date.")


def test_get_doc_metadata_date_format():
    # Arrange: Parse the sample XML into an ElementTree
    tree = ElementTree(fromstring(SAMPLE_XML))

    # Act: Call the function
    metadata = get_doc_metadata(tree)

    # Assert: Verify that the date matches the expected format (DD.MM.YYYY)
    assert re.match(DATE_REGEX, metadata.date), f"Date {metadata.date} does not match the expected format (DD.MM.YYYY)"
