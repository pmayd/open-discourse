import pytest
import regex
import pandas as pd

from open_discourse.steps.speech_content.extract import (
    process_session,
    process_period,
    get_bracket_and_prefix_from_term_number,
    get_president_pattern,
    get_minister_pattern,
    get_faction_speaker_pattern
    )

def test_president_extraction(tmp_path):
    # Arrange
    session_dir = tmp_path / "session1"
    session_dir.mkdir(exist_ok=True)
    session_file = session_dir / "session_content.txt"
    session_file.write_text(
        "Präsident Dr. Köhler: Meine Damen und Herren! Ich eröffne die 2. Sitzung des Bundestags.\n"
        "Bundespräsident Dr. Heuss: Ja, ich habe den Wunsch.\n"
    )
    # Use the president regex from extract.py via the imported function
    president_pattern = get_president_pattern()
    patterns = [president_pattern]
    save_path = tmp_path / "output"
    save_path.mkdir()

    # Act
    process_session(session_dir, patterns, save_path)

    # Assert
    df = pd.read_pickle(save_path / "session1.pkl")
    assert "name_raw" in df.columns
    assert "position_raw" in df.columns
    assert "speech_content" in df.columns
    # assert "Köhler" in df["name_raw"].values
    assert any("Köhler" in name for name in df["name_raw"])
    assert "Präsident" in df["position_raw"].values
    # assert "Heuss" in df["name_raw"].values
    assert any("Heuss" in name for name in df["name_raw"])
    assert "Bundespräsident" in df["position_raw"].values

def test_faction_speaker_extraction_pre_term10(tmp_path):
    # Arrange
    # Create the parent folder
    electoral_term_dir = tmp_path / "electoral_term_pp08"
    electoral_term_dir.mkdir(exist_ok=True)

    # Create the subfolder
    session_dir = electoral_term_dir / "08008"
    session_dir.mkdir(exist_ok=True)

    # Create the session content file inside the subfolder
    session_file = session_dir / "session_content.txt"
    session_file.write_text(
        "Vizepräsidentin Frau Renger: Bitte, fahren Sie fort.\n"
        "Sund (SPD): Die Bundesregierung, sagten Sie, habe die Arbeitslosigkeit verharmlost. "
        "Sozialdemokraten, Herr Kollege Katzer, wissen, was Arbeitslosigkeit bedeutet. Warum wollen wir denn "
        "ein Recht auf Arbeit? Das erreichen wir aber nicht mit plakativen Forderungen, sondern durch eine "
        "mühsame und praktische Politik, in der es darum geht, Zug um Zug die Vollbeschäftigung herzustellen, "
        "und dies unter Bedingungen, die nicht einfach sind. Das wissen Sie so gut wie wir.\n"
        "(Zurufe von der CDU/CSU)\n"
    )

    term_number = int(session_dir.stem[:2])  # '08' -> 8
    print(term_number) # not the issue
    open_brackets, close_brackets, prefix = get_bracket_and_prefix_from_term_number(session_dir.parent)
    print(open_brackets, close_brackets, prefix)

    faction_speaker_pattern = get_faction_speaker_pattern(
        term_number,
        session_dir,
        open_brackets,
        close_brackets,
        prefix
    )

    patterns = [faction_speaker_pattern]
    save_path = tmp_path / "output"
    save_path.mkdir()

    # Act
    process_session(session_dir, patterns, save_path)

    # Assert
    df = pd.read_pickle(save_path / "08008.pkl")
    assert "name_raw" in df.columns
    assert "position_raw" in df.columns
    assert "constituency" in df.columns
    print("Extracted names:", df["name_raw"].tolist())
    assert "Sund" in df["name_raw"].values
    assert "SPD" in df["position_raw"].values

def test_faction_speaker_extraction_pre_term10_withtitle(tmp_path):
    # Arrange
    # Create the parent folder
    electoral_term_dir = tmp_path / "electoral_term_pp08"
    electoral_term_dir.mkdir(exist_ok=True)

    # Create the subfolder
    session_dir = electoral_term_dir / "08008"
    session_dir.mkdir(exist_ok=True)

    # Create the session content file inside the subfolder
    session_file = session_dir / "session_content.txt"
    session_file.write_text(
        "(Beifall bei der SPD)\n"
        "Vizepräsident Stücklen: Das Wort hat Graf Lambsdorff.\n"
        "Dr. Graf Lambsdorff (FDP): Herr Präsident! Meine sehr verehrten Damen! Meine Herren! "
        "Leider hat es diesmal der Ablauf des politischen Zeitgeschehens erstens so mitgebracht, "
        "daß wir uns etwas reichlich weit vom Wahltermin entfernt haben, was den Eindruck aufkommen läßt, "
        "der eine oder andere hätte bei dieser Debatte bereits das Ergebnis vergessen. "
        "Zweitens hat es der zeitliche Ablauf so mit sich gebracht, daß wir heute eine Reihe von "
        "Themenkomplexen zu erörtern haben, die in einem inneren Zusammenhang stehen.\n"
    )

    term_number = int(session_dir.stem[:2])  # '08' -> 8
    print(term_number) # not the issue
    open_brackets, close_brackets, prefix = get_bracket_and_prefix_from_term_number(session_dir.parent)
    print(open_brackets, close_brackets, prefix)

    faction_speaker_pattern = get_faction_speaker_pattern(
        term_number,
        session_dir,
        open_brackets,
        close_brackets,
        prefix
    )

    patterns = [faction_speaker_pattern]
    save_path = tmp_path / "output"
    save_path.mkdir()

    # Act
    process_session(session_dir, patterns, save_path)

    # Assert
    df = pd.read_pickle(save_path / "08008.pkl")
    assert "name_raw" in df.columns
    assert "position_raw" in df.columns
    assert "constituency" in df.columns
    print("Extracted names:", df["name_raw"].tolist())
    assert "Dr. Graf Lambsdorff" in df["name_raw"].values
    assert "FDP" in df["position_raw"].values

def test_faction_speaker_extraction_with_post_term10(tmp_path):
    # Arrange
    # Create the parent folder
    electoral_term_dir = tmp_path / "electoral_term_pp14"
    electoral_term_dir.mkdir(exist_ok=True)

    # Create the subfolder
    session_dir = electoral_term_dir / "14007"
    session_dir.mkdir(exist_ok=True)

    session_file = session_dir / "session_content.txt"
    session_file.write_text(
        "Das Wort hat der Herr Abgeordnete Brandt.\n"
        "Norbert Hauser (Bonn) (CDU/CSU): Herr Bundesminister, es ist."
    )

    term_number = int(session_dir.stem[:2])  # '14'
    print(term_number)
    print("Folder Path Stem:", session_dir.parent.stem)
    print("Folder Path Stem:", electoral_term_dir.stem)

    open_brackets, close_brackets, prefix = get_bracket_and_prefix_from_term_number(session_dir.parent)
    print(open_brackets, close_brackets, prefix)

    faction_speaker_pattern = get_faction_speaker_pattern(
        term_number,
        session_dir,
        open_brackets,
        close_brackets,
        prefix
    )

    patterns = [faction_speaker_pattern]
    save_path = tmp_path / "output"
    save_path.mkdir()

    # Act
    process_session(session_dir, patterns, save_path)

    # Assert
    df = pd.read_pickle(save_path / "14007.pkl")
    assert "name_raw" in df.columns
    assert "position_raw" in df.columns
    assert "constituency" in df.columns
    print("Extracted names:", df["name_raw"].tolist())

    assert "Norbert Hauser" in df["name_raw"].values
    assert "CDU/CSU" in df["position_raw"].values
    assert "Bonn" in df["constituency"].values
