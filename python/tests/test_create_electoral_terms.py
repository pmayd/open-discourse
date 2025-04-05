import pytest

from open_discourse.helper.create_electoral_terms import create_electoral_terms


def test_create_electoral_terms():
    result = create_electoral_terms()
    assert result[12]["start_date"] == "1990-12-20"
    assert result[12]["end_date"] == "1994-11-09"
    assert result[12]["number_of_sessions"] == 243


def test_create_electoral_terms_error():
    # Access invalid electoral term
    result = create_electoral_terms()
    with pytest.raises(KeyError):
        assert result[0]["start_date"] == "1990-12-20"
    with pytest.raises(KeyError):
        assert result["12"]["start_date"] == "1990-12-20"
