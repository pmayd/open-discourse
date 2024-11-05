import pytest

from open_discourse.helper_functions.clean_text import clean


def test_clean_replaces_misrecognized_characters():
    input_text = "  — – •"
    expected_output = "- - - - "
    assert clean(input_text, remove_pdf_header=False) == expected_output


def test_clean_removes_pdf_header():
    input_text = "Deutscher Bundestag - 19. Wahlperiode - 123. Sitzung, Berlin, den 12. März 2020\nSome text"
    expected_output = "\n\nSome text"
    assert clean(input_text, remove_pdf_header=True) == expected_output

    input_test = """Das steht auch im Einklang mit den Beschlüssen, die in dieser Organisation mehrfach ge-
Deutscher Bundestag — 6. Wahlperiode — 21. Sitzung. Bonn, Freitag, den 12. Dezember 1969	753
faßt worden sind."""
    expected_output = """Das steht auch im Einklang mit den Beschlüssen, die in dieser Organisation mehrfach gefaßt worden sind."""
    assert clean(input_test, remove_pdf_header=True) == expected_output


def test_clean_removes_delimiter():
    input_text = "This is a test-\ntext"
    expected_output = "This is a testtext"
    assert clean(input_text, remove_pdf_header=False) == expected_output


def test_clean_deletes_newlines_in_brackets():
    input_text = "This is a (test\ntext) with (multiple\nlines)"
    expected_output = "This is a (test text) with (multiple lines)"
    assert clean(input_text, remove_pdf_header=False) == expected_output


def test_clean_combined():
    input_text = "  — – •\nDeutscher Bundestag - 19. Wahlperiode - 123. Sitzung, Berlin, den 12. März 2020\nThis is a test-\ntext with (multiple\nlines)"
    expected_output = "- - - - \n\n\nThis is a testtext with (multiple lines)"
    assert clean(input_text, remove_pdf_header=True) == expected_output
