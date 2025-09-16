import pytest

from open_discourse.steps.speech_content.extract import (
    get_bracket_and_prefix_from_term_number,
    get_president_pattern,
    get_minister_pattern,
    get_faction_speaker_pattern,
)

def test_bracket_extraction_term_8(tmp_path):
    """Test bracket extraction for term <= 10"""
    folder = tmp_path / "electoral_term_pp08"
    folder.mkdir()

    open_brackets, close_brackets, prefix = get_bracket_and_prefix_from_term_number(folder)

    assert open_brackets == r"[({\[]"
    assert close_brackets == r"[)}\]]"
    assert prefix == r"(?<=\n)"

def test_bracket_extraction_term_14(tmp_path):
    """Test bracket extraction for 10 < term <= 19"""
    folder = tmp_path / "electoral_term_pp14"
    folder.mkdir()

    open_brackets, close_brackets, prefix = get_bracket_and_prefix_from_term_number(folder)

    assert open_brackets == r"[(]"
    assert close_brackets == r"[)]"
    assert prefix == r"(?<=\n)"

def test_invalid_folder(tmp_path):
    """Test with non-existent folder"""
    folder = tmp_path / "nonexistent"

    open_brackets, close_brackets, prefix = get_bracket_and_prefix_from_term_number(folder)

    assert open_brackets == ""
    assert close_brackets == ""
    assert prefix == ""


def test_president_pattern_matches():
    """Test that president pattern correctly matches various president titles"""
    pattern = get_president_pattern()

    test_cases = [
        ("Präsident Dr. Köhler: Meine Damen", ("Präsident", "Dr. Köhler")),
        ("Bundespräsident Dr. Heuss: Ja, ich", ("Bundespräsident", "Dr. Heuss")),
        ("Vizepräsident Frau Renger: Zusatzfrage", ("Vizepräsident", "Frau Renger")),
        ("Präsidentin Müller: Guten Tag", ("Präsidentin", "Müller")),
        ("Vizepräsidentin Schmidt: Danke", ("Vizepräsidentin", "Schmidt")),
        ("Alterspräsident Otto Schily: Herzlich willkommen", ("Alterspräsident", "Otto Schily")),
        ("Bundeskanzler Schröder: Sehr geehrte Damen und Herren", ("Bundeskanzler", "Schröder")),
        ("Bundeskanzlerin Merkel: Liebe Kolleginnen und Kollegen", ("Bundeskanzlerin", "Merkel"))
    ]

    for text, expected in test_cases:
        match = pattern.search(text)
        assert match is not None, f"Pattern should match: {text}"
        assert match.group("position_raw") == expected[0]
        assert match.group("name_raw") == expected[1]

def test_president_pattern_no_matches():
    """Test cases that should not match president pattern"""
    pattern = get_president_pattern()

    non_matching_cases = [
        "Sund (SPD): Die Bundesregierung",
        "Dr. Vogel, Bundesminister der Justiz:",
        "Normal text without titles",
    ]

    for text in non_matching_cases:
        match = pattern.search(text)
        assert match is None, f"Pattern should not match: {text}"

def test_minister_pattern_bundesminister():
    """Test minister pattern for Bundesminister"""
    pattern = get_minister_pattern(r"[({\[]", r"[)}\]]", r"(?<=\n)")

    test_text = "\nDr. Vogel, Bundesminister der Justiz: Herr Präsident! Meine sehr verehrten Damen und Herren!"
    match = pattern.search(test_text)

    assert match is not None
    assert match.group("name_raw") == "Dr. Vogel"
    assert match.group("position_raw") == "Bundesminister der Justiz"


def test_minister_pattern_bundesministerin():
    """Test minister pattern for Bundesministerin (female form)"""
    pattern = get_minister_pattern(r"[({\[]", r"[)}\]]", r"(?<=\n)")

    test_text = "\nFrau Schmidt, Bundesministerin für Bildung: Sehr geehrte Damen und Herren!"
    match = pattern.search(test_text)

    assert match is not None
    assert match.group("name_raw") == "Frau Schmidt"
    assert match.group("position_raw") == "Bundesministerin für Bildung"


def test_minister_pattern_staatsminister():
    """Test minister pattern for Staatsminister"""
    pattern = get_minister_pattern(r"[({\[]", r"[)}\]]", r"(?<=\n)")

    test_text = "\nHuonker, Staatsminister beim Bundeskanzler: Herr Kollege, ich beantworte die Frage mit Nein."
    match = pattern.search(test_text)

    assert match is not None
    assert match.group("name_raw") == "Huonker"
    assert match.group("position_raw") == "Staatsminister beim Bundeskanzler"


def test_minister_pattern_staatssekretaer():
    """Test minister pattern for Staatssekretär"""
    pattern = get_minister_pattern(r"[({\[]", r"[)}\]]", r"(?<=\n)")

    test_text = "\nMüller, Staatssekretär im Bundesministerium: Das ist eine wichtige Frage."
    match = pattern.search(test_text)

    assert match is not None
    assert match.group("name_raw") == "Müller"
    assert match.group("position_raw") == "Staatssekretär im Bundesministerium"


def test_minister_pattern_parl_staatssekretaer():
    """Test minister pattern for Parl. Staatssekretär"""
    pattern = get_minister_pattern(r"[({\[]", r"[)}\]]", r"(?<=\n)")

    test_text = "\nGallus, Parl. Staatssekretär beim Bundesminister für Ernährung, Landwirtschaft und Forsten: Herr Kollege Eigen, die Erzeugung von Zucker in der"
    match = pattern.search(test_text)

    assert match is not None
    assert match.group("name_raw") == "Gallus"
    assert match.group("position_raw") == "Parl. Staatssekretär beim Bundesminister für Ernährung, Landwirtschaft und Forsten"


def test_minister_pattern_praesident():
    """Test minister pattern for Präsident (in minister context)"""
    pattern = get_minister_pattern(r"[({\[]", r"[)}\]]", r"(?<=\n)")

    test_text = "\nDr. Klein, Präsident des Bundesamtes: Ich kann diese Frage beantworten."
    match = pattern.search(test_text)

    assert match is not None
    assert match.group("name_raw") == "Dr. Klein"
    assert match.group("position_raw") == "Präsident des Bundesamtes"


def test_minister_pattern_bundeskanzler():
    """Test minister pattern for Bundeskanzler"""
    pattern = get_minister_pattern(r"[({\[]", r"[)}\]]", r"(?<=\n)")

    test_text = "\nSchmidt, Bundeskanzler: Meine Damen und Herren, wir beginnen mit der Debatte."
    match = pattern.search(test_text)

    assert match is not None
    assert match.group("name_raw") == "Schmidt"
    assert match.group("position_raw") == "Bundeskanzler"


def test_minister_pattern_bundeskanzlerin():
    """Test minister pattern for Bundeskanzlerin"""
    pattern = get_minister_pattern(r"[({\[]", r"[)}\]]", r"(?<=\n)")

    test_text = "\nFrau Merkel, Bundeskanzlerin: Wir kommen zur nächsten Tagesordnung."
    match = pattern.search(test_text)

    assert match is not None
    assert match.group("name_raw") == "Frau Merkel"
    assert match.group("position_raw") == "Bundeskanzlerin"

def test_minister_pattern_schriftfuehrerin():
    """Test minister pattern for Schriftführerin"""
    pattern = get_minister_pattern(r"[({\[]", r"[)}\]]", r"(?<=\n)")

    test_text = "\nFrau Schulz, Schriftführerin: Bitte notieren Sie die Beschlüsse."
    match = pattern.search(test_text)

    assert match is not None
    assert match.group("name_raw") == "Frau Schulz"
    assert match.group("position_raw") == "Schriftführerin"


def test_minister_pattern_senator():
    """Test minister pattern for Senator"""
    pattern = get_minister_pattern(r"[({\[]", r"[)}\]]", r"(?<=\n)")

    test_text = "\nFischer, Senator: Ich habe eine Erklärung abzugeben."
    match = pattern.search(test_text)

    assert match is not None
    assert match.group("name_raw") == "Fischer"
    assert match.group("position_raw") == "Senator"


def test_minister_pattern_senator_with_constituency():
    """Test minister pattern for Senator with constituency"""
    pattern = get_minister_pattern(r"[({\[]", r"[)}\]]", r"(?<=\n)")

    test_text = "\nWagner, Senator (Berlin): Die Länder haben dazu eine klare Position."
    match = pattern.search(test_text)

    assert match is not None
    assert match.group("name_raw") == "Wagner"
    assert match.group("position_raw") == "Senator (Berlin)"
    assert match.group("constituency") == "Berlin"

def test_minister_pattern_berichterstatter():
    """Test minister pattern for Berichterstatter"""
    pattern = get_minister_pattern(r"[({\[]", r"[)}\]]", r"(?<=\n)")

    test_text = "\nKoch, Berichterstatter: Meine Damen und Herren! Der Ausschuss hat beraten."
    match = pattern.search(test_text)

    assert match is not None
    assert match.group("name_raw") == "Koch"
    assert match.group("position_raw") == "Berichterstatter"


'''One issue found with the get_minister_pattern function is that I found a case in which the party affiliation is include, and this Regex does not capture it:
"Zinn (SPD), Berichterstatter: Meine Damen und Herren! Gegen zwei Mitglieder des Hauses.\n" A direct quote from Session 01004 isn'extracted properly by the Regex'''

def test_faction_speaker_pattern_term8(tmp_path):
    """Test faction speaker pattern for term <= 10"""
    folder = tmp_path / "electoral_term_pp08"
    folder.mkdir()
    session_dir = folder / "08008"
    session_dir.mkdir()

    open_brackets = r"[({\[]"
    close_brackets = r"[)}\]]"
    prefix = r"(?<=\n)"

    pattern = get_faction_speaker_pattern(8, session_dir, open_brackets, close_brackets, prefix)

    test_cases = [
        ("\nMüller (CDU/CSU): Die Bundesregierung", ("Müller", "CDU/CSU")),
        ("\nSchmidt (SPD): Die Bundesregierung", ("Schmidt", "SPD")),
        ("\nWeber (F.D.P.): Die Bundesregierung", ("Weber", "F.D.P.")),
        ("\nFischer (GRÜNEN): Die Bundesregierung", ("Fischer", "GRÜNEN")),
        ("\nPetra Pau (fraktionslos): Ich:", ("Petra Pau", "fraktionslos")
)
    ]

    for text, expected in test_cases:
        match = pattern.search(text)
        assert match is not None, f"Should match: {text}"
        assert match.group("name_raw") == expected[0]
        assert match.group("position_raw") == expected[1]

def test_faction_speaker_pattern_term14(tmp_path):
    """Test faction speaker pattern for term > 10"""
    folder = tmp_path / "electoral_term_pp14"
    folder.mkdir()
    session_dir = folder / "14007"
    session_dir.mkdir()

    open_brackets = r"[(]"
    close_brackets = r"[)]"
    prefix = r"(?<=\n)"

    pattern = get_faction_speaker_pattern(14, session_dir, open_brackets, close_brackets, prefix)

    test_text = "\nNorbert Hauser (Bonn) (CDU/CSU): Herr Bundesminister"
    match = pattern.search(test_text)

    assert match is not None
    assert match.group("name_raw") == "Norbert Hauser"
    assert match.group("position_raw") == "CDU/CSU"
    assert match.group("constituency") == "Bonn"

def test_faction_speaker_pattern_no_matches(tmp_path):
    """Test cases that should not match faction speaker pattern"""
    folder = tmp_path / "electoral_term_pp08"
    folder.mkdir()
    session_dir = folder / "08008"
    session_dir.mkdir()

    open_brackets = r"[({\[]"
    close_brackets = r"[)}\]]"
    prefix = r"(?<=\n)"

    pattern = get_faction_speaker_pattern(8, session_dir, open_brackets, close_brackets, prefix)

    non_matching_cases = [
        "Präsident Dr. Köhler: Meine Damen",
        "Dr. Vogel, Bundesminister der Justiz:",
        "Normal text without patterns",
        "lowercase name (SPD): should not match",
    ]

    for text in non_matching_cases:
        match = pattern.search(text)
        assert match is None, f"Pattern should not match: {text}"
