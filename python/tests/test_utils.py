from pathlib import Path

import pytest

from open_discourse.helper_functions.utils import get_term_from_path
import pyparsing as pp


term_number_parser = pp.Literal("electoral_term") + "_" + pp.Word(pp.nums, exact=2)


@pytest.mark.parametrize(
    "folder_path, expected",
    [
        (Path("/some/path/electoral_term_12"), 12),
        (Path("/some/path/no_term"), None),
        (Path("/some/path/electoral_term_abc"), None),
        (Path("/12_electoral_term/path"), None),
        (Path("/path/electoral_term_34"), 34),
        (Path("/path/electoral_term_56/another_term_78"), 56),
    ],
)
def test_get_term_from_path(folder_path, expected):
    assert get_term_from_path(folder_path) == expected
