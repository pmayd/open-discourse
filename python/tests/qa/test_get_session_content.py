import xml.etree.ElementTree as et
from pathlib import Path

import pytest

from open_discourse.definitions.path_definitions import RAW_XML
from open_discourse.helper_functions.clean_text import clean
from open_discourse.helper_functions.parser import get_session_content

DATA_FOLDER = RAW_XML


def xml_files():
    return list((DATA_FOLDER / "electoral_term_pp01.zip").glob("*.xml")) + list(
        (DATA_FOLDER / "electoral_term_pp02.zip").glob("*.xml")
    )


@pytest.mark.qa
@pytest.mark.parametrize("file_path", xml_files())
def test_get_session_content(file_path):
    tree = et.parse(file_path)
    text_corpus = tree.find("TEXT").text

    # Clean text corpus.
    text_corpus = clean(text_corpus)

    text_corpus += "\n\nEND OF FILE"

    session_content = get_session_content(text_corpus)

    assert session_content != "", f"Session content should not be empty for {file_path}"
