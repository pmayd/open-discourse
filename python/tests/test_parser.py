import pytest

from open_discourse.helper_functions.parser import get_session_content


@pytest.mark.parametrize(
    "text_corpus, expected",
    [
        (
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
        )
    ],
)
def test_get_session_content(text_corpus, expected):
    assert get_session_content(text_corpus) == expected
