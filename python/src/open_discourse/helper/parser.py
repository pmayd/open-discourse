from xml.etree.ElementTree import ElementTree

import regex
from pydantic import BaseModel

# A gap inside a single (possibly line-wrapped) statement: length-capped,
# may cross one line break but never a blank line, and stops at sentence
# boundaries. A period only counts as a sentence boundary when it follows
# an ordinary word (>= 4 lowercase letters) and precedes an uppercase
# letter — abbreviations ("Dr.", "D.", "h. c."), numbers ("2. Wahlperiode")
# and OCR noise ("Minuten. durch") pass through.
_GAP = r"(?:[^.!?\n]|(?<!\p{Ll}{4})\.|\.(?!\s*\p{Lu})|\n(?!\s*\n)){0,200}?"
# A gap inside a single-line parenthetical.
_PAREN_GAP = r"[^)\n]{0,200}?"

BEGIN_PATTERN = regex.compile(
    rf"Die\b{_GAP}\bSitzung{_GAP}wird{_GAP}\d{{1,2}}{_GAP}Uhr{_GAP}"
    rf"(?:eröffnet|eingeleitet|wieder\s?aufgenommen)"
)

APPENDIX_PATTERN = regex.compile(
    rf"\((?:Schluß|Schluss){_PAREN_GAP}Sitzung{_PAREN_GAP}Uhr{_PAREN_GAP}\)"
)


class Metadata(BaseModel):
    document_number: str
    date: str


def get_session_content(text_corpus: str) -> str:
    """
    Extracts the spoken content from the text corpus.

    Session openings ("Die Sitzung wird um ... Uhr eröffnet/eingeleitet/
    wieder aufgenommen", possibly wrapped across a line break) and endings
    ("(Schluß/Schluss der Sitzung: ... Uhr ...)") are paired positionally:
    each ending consumes the first opening that follows the previous ending,
    so the table of contents and appendix between an ending and the next
    day's opening of an interrupted session are excluded. An opening with no
    ending after it (session without a formal ending) is sliced to the end
    of the corpus, or to an "END OF FILE" marker if the caller appended one.

    Args:
        text_corpus (str): The text corpus to extract the spoken content from.

    Returns:
        str: The spoken content if it could be extracted. Otherwise, an empty string.
    """
    find_beginnings = list(BEGIN_PATTERN.finditer(text_corpus))
    find_endings = list(APPENDIX_PATTERN.finditer(text_corpus))

    segments = []
    last_end = 0
    for ending in find_endings:
        begin = next(
            (b for b in find_beginnings if last_end < b.end() <= ending.start()),
            None,
        )
        if begin is None:
            # Ending without a new opening before it (duplicate or false match).
            continue
        segments.append(text_corpus[begin.end() : ending.start()])
        last_end = ending.end()

    # Unterminated tail: an opening after the last paired ending.
    tail = next((b for b in find_beginnings if b.start() >= last_end), None)
    if tail is not None:
        eof_pos = text_corpus.find("END OF FILE", tail.end())
        stop = eof_pos if eof_pos != -1 else len(text_corpus)
        segments.append(text_corpus[tail.end() : stop])

    session_content = "".join(segments)

    if not session_content:
        print(
            f"No session content found. Beginnings: {len(find_beginnings)}, Endings: {len(find_endings)}"
        )

    return session_content


def get_doc_metadata(tree: ElementTree) -> Metadata:
    """
    Extracts the document number and the date of the session from the XML tree.

    Args:
        tree (ElementTree): The XML tree to extract the metadata from.

    Returns:
        Metadata: The document number and the date of the session.
    """
    # Get the document number, the date of the session and the content.
    document_number = tree.find("NR").text
    date = tree.find("DATUM").text

    return Metadata(document_number=document_number, date=date)
