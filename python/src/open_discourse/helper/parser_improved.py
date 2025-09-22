from xml.etree.ElementTree import ElementTree

import regex
from pydantic import BaseModel

# Improved patterns that handle newlines and alternative words
BEGIN_PATTERN = regex.compile(
    r"Die[^\.]*?Sitzung[^\.]*?wird[^\.]*?\d{1,2}[^\.]*?Uhr[^\.]*?"
    r"(durch[^\.]*?den.*?)?(eröffnet|eingeleitet|wieder\s*aufgenommen)[^\.]*?[.]?",
    regex.V0 | regex.DOTALL
)

APPENDIX_PATTERN = regex.compile(
    r"\((?:Schluß|Schluss)[^)]*?Sitzung[^)]*?Uhr[^)]*?\)"
)

INTERRUPTION_PATTERN = regex.compile(
    r"\(Unterbrechung[^)]*?Sitzung[^)]*?\)",
    regex.V0 | regex.DOTALL
)


class Metadata(BaseModel):
    document_number: str
    date: str


def get_session_content(text_corpus: str) -> str:
    """
    Extracts the spoken content from the text corpus.

    Improved version that handles:
    - Newlines in session opening statements
    - Alternative opening words (eröffnet, eingeleitet, wieder aufgenommen)
    - Session interruptions and resumptions

    Args:
        text_corpus (str): The text corpus to extract the spoken content from.

    Returns:
        str: The spoken content if it could be extracted. Otherwise, an empty string.
    """
    find_beginnings = list(BEGIN_PATTERN.finditer(text_corpus))
    find_endings = list(APPENDIX_PATTERN.finditer(text_corpus))
    find_interruptions = list(INTERRUPTION_PATTERN.finditer(text_corpus))

    session_content = ""

    if not find_beginnings:
        print(
            f"No session content found. Beginnings: {len(find_beginnings)}, Endings: {len(find_endings)}"
        )
        return ""

    # Strategy 1: If there are interruptions, extract from first beginning to last ending
    if find_interruptions and find_endings:
        session_content = text_corpus[
            find_beginnings[0].span()[1] : find_endings[-1].span()[0]
        ]

    # Strategy 2: More beginnings than endings with exactly one ending
    elif len(find_beginnings) > len(find_endings) and len(find_endings) == 1:
        session_content = text_corpus[
            find_beginnings[0].span()[1] : find_endings[0].span()[0]
        ]

    # Strategy 3: More beginnings than endings with multiple endings (handle interruptions)
    elif len(find_beginnings) > len(find_endings) and len(find_endings) > 1:
        # Extract from first beginning to last ending
        session_content = text_corpus[
            find_beginnings[0].span()[1] : find_endings[-1].span()[0]
        ]

    # Strategy 4: Equal beginnings and endings
    elif len(find_beginnings) == len(find_endings) and find_endings:
        for begin, end in zip(find_beginnings, find_endings):
            session_content += text_corpus[begin.span()[1] : end.span()[0]]

    # Strategy 5: Beginnings but no endings - use EOF marker if available
    elif find_beginnings and not find_endings:
        eof_pos = text_corpus.find("END OF FILE")
        if eof_pos > 0:
            session_content = text_corpus[find_beginnings[0].span()[1] : eof_pos]
        else:
            print(
                f"No session content found. Beginnings: {len(find_beginnings)}, Endings: {len(find_endings)}"
            )
    else:
        print(
            f"No session content found. Beginnings: {len(find_beginnings)}, Endings: {len(find_endings)}"
        )

    return session_content.strip() if session_content else ""


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