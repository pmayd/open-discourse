import pytest

from open_discourse.steps.speech_content.extract import (
    get_bracket_and_prefix_from_term_number,
    get_president_pattern,
    get_minister_pattern,
    get_faction_speaker_pattern,
)

@pytest.mark.parametrize(
    "folder_name, expected_open, expected_close, expected_prefix",
    [
        ("electoral_term_pp08", r"[({\[]", r"[)}\]]", r"(?<=\n)"),
        ("electoral_term_pp14", r"[(]", r"[)]", r"(?<=\n)"),
        ("electoral_term_pp05", r"[({\[]", r"[)}\]]", r"(?<=\n)"),
        ("electoral_term_pp19", r"[(]", r"[)]", r"(?<=\n)"),
    ],
)
def test_bracket_extraction_valid_terms(tmp_path, folder_name, expected_open, expected_close, expected_prefix):
    """Test bracket extraction for various valid terms"""
    folder = tmp_path / folder_name
    folder.mkdir()

    open_brackets, close_brackets, prefix = get_bracket_and_prefix_from_term_number(folder)

    assert open_brackets == expected_open
    assert close_brackets == expected_close
    assert prefix == expected_prefix


def test_invalid_folder(tmp_path):
    """Test with non-existent folder"""
    folder = tmp_path / "nonexistent"

    open_brackets, close_brackets, prefix = get_bracket_and_prefix_from_term_number(folder)

    assert open_brackets == ""
    assert close_brackets == ""
    assert prefix == ""

@pytest.mark.parametrize(
    "text, expected_position, expected_name",
    [
        ("Präsident Dr. Köhler: Meine Damen", "Präsident", "Dr. Köhler"),
        ("Bundespräsident Dr. Heuss: Ja, ich", "Bundespräsident", "Dr. Heuss"),
        ("Vizepräsident Frau Renger: Zusatzfrage", "Vizepräsident", "Frau Renger"),
        ("Präsidentin Müller: Guten Tag", "Präsidentin", "Müller"),
        ("Vizepräsidentin Schmidt: Danke", "Vizepräsidentin", "Schmidt"),
        ("Alterspräsident Otto Schily: Herzlich willkommen", "Alterspräsident", "Otto Schily"),
        ("Bundeskanzler Schröder: Sehr geehrte Damen und Herren", "Bundeskanzler", "Schröder"),
        ("Bundeskanzlerin Merkel: Liebe Kolleginnen und Kollegen", "Bundeskanzlerin", "Merkel"),
    ],
)
def test_president_pattern_matches(text, expected_position, expected_name):
    """Test that president pattern correctly matches various president titles"""
    pattern = get_president_pattern()
    match = pattern.search(text)

    assert match is not None, f"Pattern should match: {text}"
    assert match.group("position_raw") == expected_position
    assert match.group("name_raw") == expected_name


@pytest.mark.parametrize(
    "text",
    [
        "Sund (SPD): Die Bundesregierung",
        "Dr. Vogel, Bundesminister der Justiz:",
        "Normal text without titles",
        "lowercase präsident: should not match",
    ],
)
def test_president_pattern_no_matches(text):
    """Test cases that should not match president pattern"""
    pattern = get_president_pattern()
    match = pattern.search(text)
    assert match is None, f"Pattern should not match: {text}"


@pytest.fixture
def minister_pattern():
    """Fixture to provide minister pattern with standard brackets"""
    return get_minister_pattern(r"[({\[]", r"[)}\]]", r"(?<=\n)")

@pytest.mark.parametrize(
    "test_text, expected_name, expected_position, expected_constituency",
    [
        (
            "\nDr. Vogel, Bundesminister der Justiz: Herr Präsident!",
            "Dr. Vogel",
            "Bundesminister der Justiz",
            None,
        ),
        (
            "\nFrau Schmidt, Bundesministerin für Bildung: Sehr geehrte Damen!",
            "Frau Schmidt",
            "Bundesministerin für Bildung",
            None,
        ),
        (
            "\nHuonker, Staatsminister beim Bundeskanzler: Herr Kollege",
            "Huonker",
            "Staatsminister beim Bundeskanzler",
            None,
        ),
        (
            "\nMüller, Staatssekretär im Bundesministerium: Das ist wichtig.",
            "Müller",
            "Staatssekretär im Bundesministerium",
            None,
        ),
        (
            "\nGallus, Parl. Staatssekretär beim Bundesminister für Ernährung, Landwirtschaft und Forsten: Herr Kollege",
            "Gallus",
            "Parl. Staatssekretär beim Bundesminister für Ernährung, Landwirtschaft und Forsten",
            None,
        ),
        (
            "\nDr. Klein, Präsident des Bundesamtes: Ich kann antworten.",
            "Dr. Klein",
            "Präsident des Bundesamtes",
            None,
        ),
        (
            "\nSchmidt, Bundeskanzler: Meine Damen und Herren",
            "Schmidt",
            "Bundeskanzler",
            None,
        ),
        (
            "\nFrau Merkel, Bundeskanzlerin: Wir kommen zur nächsten Tagesordnung.",
            "Frau Merkel",
            "Bundeskanzlerin",
            None,
        ),
        (
            "\nFrau Schulz, Schriftführerin: Bitte notieren Sie die Beschlüsse.",
            "Frau Schulz",
            "Schriftführerin",
            None,
        ),
        (
            "\nFischer, Senator: Ich habe eine Erklärung abzugeben.",
            "Fischer",
            "Senator",
            None,
        ),
        (
            "\nWagner, Senator (Berlin): Die Länder haben eine klare Position.",
            "Wagner",
            "Senator (Berlin)",
            "Berlin",
        ),
        (
            "\nKoch, Berichterstatter: Meine Damen und Herren! Der Ausschuss hat beraten.",
            "Koch",
            "Berichterstatter",
            None,
        ),
    ],
)
def test_minister_pattern(minister_pattern, test_text, expected_name, expected_position, expected_constituency):
    """Test minister pattern for all supported titles"""
    match = minister_pattern.search(test_text)

    assert match is not None, f"Pattern should match: {test_text}"
    assert match.group("name_raw") == expected_name
    assert match.group("position_raw") == expected_position

    if expected_constituency:
        assert match.group("constituency") == expected_constituency
    else:
        try:
            constituency = match.group("constituency")
            assert constituency is None
        except IndexError: # IndexError is expected when constituency group doesn't exist
            pass

@pytest.mark.parametrize(
    "test_text, reason",
    [
        (
            "\nZinn (SPD), Berichterstatter: Meine Damen und Herren! Gegen zwei Mitglieder des Hauses.",
            "Party affiliation before position not supported"
        )
    ],
)
def test_minister_pattern_known_limitations(minister_pattern, test_text, reason):
    """Test for known limitations with party affiliation in minister pattern"""
    match = minister_pattern.search(test_text)

    # Document the current behavior - these should be improved in the future
    assert match is None, f"Current regex limitation: {reason}"


@pytest.fixture
def faction_speaker_pattern_term8(tmp_path):
    """Fixture for faction speaker pattern for term 8"""
    folder = tmp_path / "electoral_term_pp08"
    folder.mkdir()
    session_dir = folder / "08008"
    session_dir.mkdir()

    return get_faction_speaker_pattern(8, session_dir, r"[({\[]", r"[)}\]]", r"(?<=\n)")


@pytest.fixture
def faction_speaker_pattern_term14(tmp_path):
    """Fixture for faction speaker pattern for term 14"""
    folder = tmp_path / "electoral_term_pp14"
    folder.mkdir()
    session_dir = folder / "14007"
    session_dir.mkdir()

    return get_faction_speaker_pattern(14, session_dir, r"[(]", r"[)]", r"(?<=\n)")

@pytest.mark.parametrize(
    "text, expected_name, expected_party",
    [
        ("\nMüller (CDU/CSU): Die Bundesregierung", "Müller", "CDU/CSU"),
        ("\nSchmidt (SPD): Die Bundesregierung", "Schmidt", "SPD"),
        ("\nWeber (F.D.P.): Die Bundesregierung", "Weber", "F.D.P."),
        ("\nFischer (GRÜNEN): Die Bundesregierung", "Fischer", "GRÜNEN"),
        ("\nPetra Pau (fraktionslos): Ich:", "Petra Pau", "fraktionslos"),
        ("\nHans-Christian Ströbele (GRÜNEN): Meine Damen", "Hans-Christian Ströbele", "GRÜNEN"),
    ],
)
def test_faction_speaker_pattern_term8(faction_speaker_pattern_term8, text, expected_name, expected_party):
    """Test faction speaker pattern for term <= 10"""
    match = faction_speaker_pattern_term8.search(text)

    assert match is not None, f"Should match: {text}"
    assert match.group("name_raw") == expected_name
    assert match.group("position_raw") == expected_party



@pytest.mark.parametrize(
    "text, expected_name, expected_party, expected_constituency",
    [
        (
            "\nNorbert Hauser (Bonn) (CDU/CSU): Herr Bundesminister",
            "Norbert Hauser",
            "CDU/CSU",
            "Bonn",
        )
    ]
)
def test_faction_speaker_pattern_term14_with_constituency(faction_speaker_pattern_term14, text, expected_name, expected_party, expected_constituency):
    """Test faction speaker pattern for term > 10 with constituency"""
    match = faction_speaker_pattern_term14.search(text)

    assert match is not None, f"Should match: {text}"
    assert match.group("name_raw") == expected_name
    assert match.group("position_raw") == expected_party
    assert match.group("constituency") == expected_constituency


@pytest.mark.parametrize(
    "text",
    [
        "Präsident Dr. Köhler: Meine Damen",
        "Dr. Vogel, Bundesminister der Justiz:",
        "Normal text without patterns",
        "lowercase name (SPD): should not match",
        "Name without brackets: should not match",
    ],
)
def test_faction_speaker_pattern_no_matches(faction_speaker_pattern_term8, text):
    """Test cases that should not match faction speaker pattern"""
    match = faction_speaker_pattern_term8.search(text)
    assert match is None, f"Pattern should not match: {text}"
