import regex


BEGIN_PATTERN = regex.compile(
    r"Die.*?Sitzung.*?wird.*?\d{1,2}.*?Uhr.*?(durch.*?den.*?)?eröffnet"
)

APPENDIX_PATTERN = regex.compile(r"\(Schluß.*?Sitzung.*?Uhr.*?\)")


def get_session_content(text_corpus: str) -> str:
    """
    Extracts the spoken content from the text corpus.

    Description:
    If the number of beginnings is greater than the number of endings, the spoken content is extracted from the first beginning to the first ending.
    If the number of beginnings is equal to the number of endings, the spoken content is extracted from the first beginning to the first ending, the second beginning to the second ending, and so on.

    Args:
        text_corpus (str): The text corpus to extract the spoken content from.

    Returns:
        str: The spoken content if it could be extracted. Otherwise, an empty string.
    """
    find_beginnings = list(BEGIN_PATTERN.finditer(text_corpus))
    find_endings = list(APPENDIX_PATTERN.finditer(text_corpus))

    # Just extract spoken parts between the matching of the
    # beginning and the ending pattern. TOC and APPENDIX is
    # disregarded. For example: If a session is interrupted and
    # continued on the next day, there is again a whole table of content
    # section with the names of all the speakers, which should not be
    # included in the usual spoken content.
    session_content = ""
    if len(find_beginnings) > len(find_endings) and len(find_endings) == 1:
        session_content = text_corpus[
            find_beginnings[0].span()[1] : find_endings[0].span()[0]
        ]
    elif len(find_beginnings) == len(find_endings):
        for begin, end in zip(find_beginnings, find_endings):
            session_content += text_corpus[begin.span()[1] : end.span()[0]]

    return session_content
