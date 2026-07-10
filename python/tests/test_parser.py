import pytest

from open_discourse.helper.parser import get_session_content


@pytest.mark.parametrize(
    "text_corpus, expected",
    [
        pytest.param(
            """2. Sitzung.
Bonn, Montag, den 12. September 1949.
Eidesleistung des Bundespräsidenten . . . 9A
Ansprache des Bundespräsidenten Dr. Heuss 9C
Schlußworte des Präsidenten Dr. Köhler . 11D
Die Sitzung wird um 19 Uhr 18 Minuten durch den Präsidenten Dr. Köhler eröffnet.
Wir werden nunmehr den Herrn Bundespräsidenten hinausgeleiten.
Ich schließe die Sitzung.
(Schluß der Sitzung: 19 Uhr 43 Minuten.)""",
            """.\nWir werden nunmehr den Herrn Bundespräsidenten hinausgeleiten.
Ich schließe die Sitzung.\n""",
            id="single_session_with_toc",
        ),
        pytest.param(
            """Die Sitzung wird um 16 Uhr 16 Minuten durch
den Präsidenten Dr. Köhler eröffnet.
Ich breche die Sitzung ab und vertage auf morgen vormittag 11 Uhr.
Die Sitzung ist geschlossen.
(Schluß der Sitzung: 19 Uhr 44 Minuten.)""",
            """.\nIch breche die Sitzung ab und vertage auf morgen vormittag 11 Uhr.
Die Sitzung ist geschlossen.\n""",
            id="opening_wrapped_across_line_break",
        ),
        pytest.param(
            """Die Sitzung wird um 9 Uhr 2 Minuten durch den Vizepräsidenten Dr. Schmid eröffnet.
Test
(Schluß der Sitzung: 20 Uhr 51 Minuten.)""",
            """.\nTest\n""",
            id="trailing_newline_preserved",
        ),
        pytest.param(
            """Die Sitzung wird um 9 Uhr eröffnet.
Erster Redebeitrag.
(Schluß der Sitzung: 13 Uhr.)
Namentliche Abstimmung . . . 100A
Anlage 1: Schriftliche Antworten, die nicht gesprochen wurden.
Die Sitzung wird um 9 Uhr wieder aufgenommen.
Zweiter Redebeitrag.
(Schluß der Sitzung: 18 Uhr.)
Anlage 2: Weitere schriftliche Antworten.""",
            """.\nErster Redebeitrag.\n.\nZweiter Redebeitrag.\n""",
            id="interrupted_session_excludes_toc_and_appendix",
        ),
        pytest.param(
            """Die Sitzung wird um 9 Uhr eröffnet.
Erster Redebeitrag.
(Unterbrechung der Sitzung von 13 bis 14 Uhr.)
Die Sitzung wird um 14 Uhr wieder aufgenommen.
Zweiter Redebeitrag.
(Schluß der Sitzung: 18 Uhr.)""",
            """.\nErster Redebeitrag.
(Unterbrechung der Sitzung von 13 bis 14 Uhr.)
Die Sitzung wird um 14 Uhr wieder aufgenommen.
Zweiter Redebeitrag.\n""",
            id="same_day_interruption_without_intermediate_ending",
        ),
        pytest.param(
            """Die Sitzung wird um 9 Uhr eröffnet.
Redebeitrag ohne formales Ende.

END OF FILE""",
            """.\nRedebeitrag ohne formales Ende.\n\n""",
            id="no_ending_with_eof_marker",
        ),
        pytest.param(
            """Die Sitzung wird um 9 Uhr eröffnet.
Redebeitrag ohne formales Ende.""",
            """.\nRedebeitrag ohne formales Ende.""",
            id="no_ending_without_eof_marker",
        ),
        pytest.param(
            """Die Sitzung wird um 9 Uhr eingeleitet.
Redebeitrag.
(Schluss der Sitzung: 18 Uhr.)""",
            """.\nRedebeitrag.\n""",
            id="eingeleitet_opening_and_schluss_spelling",
        ),
        pytest.param(
            """Die Sitzung (2. Wahlperiode) wird um 9 Uhr eröffnet.
Redebeitrag.
(Schluß der Sitzung: 18 Uhr.)""",
            """.\nRedebeitrag.\n""",
            id="opening_containing_parentheses",
        ),
        pytest.param(
            """Die letzte Sitzung dieser Woche wird morgen um 14 Uhr fortgesetzt. Wir haben bereits entsprechende Schritte eingeleitet.
Weitere Debatte.""",
            "",
            id="debate_prose_is_not_an_opening",
        ),
        pytest.param(
            """Diese Sitzung des Ausschusses wird nach 9 Uhr in anderer Form wieder aufgenommen, sagte er.
Weitere Debatte.""",
            "",
            id="diese_prefix_is_not_an_opening",
        ),
        pytest.param(
            """Die Sitzung wird um 9 Uhr eröffnet.
Redebeitrag.
(Schlußabstimmung über den Antrag:
die Sitzung möge beschließen, um 18 Uhr
zu vertagen.)
Weiterer Redebeitrag.
(Schluß der Sitzung: 18 Uhr.)""",
            """.\nRedebeitrag.
(Schlußabstimmung über den Antrag:
die Sitzung möge beschließen, um 18 Uhr
zu vertagen.)
Weiterer Redebeitrag.\n""",
            id="multiline_parenthetical_is_not_an_ending",
        ),
    ],
)
def test_get_session_content(text_corpus, expected):
    assert get_session_content(text_corpus) == expected
