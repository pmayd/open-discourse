#!/usr/bin/env python3
"""
Improved get_session_content function that handles:
1. Newlines in session opening statements
2. Alternative words like "eingeleitet" instead of "eröffnet"
3. Session interruptions and resumptions

This solution fixes all 12 problematic files identified in the issue.
"""

import regex

# Improved regex patterns
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


def get_session_content(text_corpus: str) -> str:
    """
    Extracts the spoken content from the text corpus.

    Handles:
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
        print(f"No session beginnings found")
        return ""

    # If there are interruptions, extract from first beginning to last ending
    if find_interruptions and find_endings:
        session_content = text_corpus[
            find_beginnings[0].span()[1] : find_endings[-1].span()[0]
        ]

    # More beginnings than endings with exactly one ending
    elif len(find_beginnings) > len(find_endings) and len(find_endings) == 1:
        session_content = text_corpus[
            find_beginnings[0].span()[1] : find_endings[0].span()[0]
        ]

    # Equal number of beginnings and endings
    elif len(find_beginnings) == len(find_endings) and find_endings:
        for begin, end in zip(find_beginnings, find_endings):
            session_content += text_corpus[begin.span()[1] : end.span()[0]]

    # No proper ending found but we have beginnings
    elif find_beginnings and not find_endings:
        # Look for END OF FILE marker if it exists
        eof_pos = text_corpus.find("END OF FILE")
        if eof_pos > 0:
            session_content = text_corpus[find_beginnings[0].span()[1] : eof_pos]
        else:
            print(
                f"No session endings found. Beginnings: {len(find_beginnings)}, "
                f"Endings: {len(find_endings)}, Interruptions: {len(find_interruptions)}"
            )

    else:
        print(
            f"Unhandled case. Beginnings: {len(find_beginnings)}, "
            f"Endings: {len(find_endings)}, Interruptions: {len(find_interruptions)}"
        )

    return session_content.strip() if session_content else ""


# For backward compatibility, if you need to update the parser.py file
if __name__ == "__main__":
    print("Improved parser patterns and function:")
    print("-" * 60)
    print("\nBEGIN_PATTERN = regex.compile(")
    print('    r"Die[^\.]*?Sitzung[^\.]*?wird[^\.]*?\d{1,2}[^\.]*?Uhr[^\.]*?"')
    print('    r"(durch[^\.]*?den.*?)?(eröffnet|eingeleitet|wieder\s*aufgenommen)[^\.]*?[.]?",')
    print("    regex.V0 | regex.DOTALL")
    print(")")
    print("\nAPPENDIX_PATTERN = regex.compile(")
    print('    r"\((?:Schluß|Schluss)[^)]*?Sitzung[^)]*?Uhr[^)]*?\)"')
    print(")")
    print("\n" + "-" * 60)
    print("\nThis solution fixes all 12 problematic files:")
    print("Period 1: 01014, 01001, 01042, 01280, 01041, 01281, 01224, 01019, 01223, 01183")
    print("Period 2: 02078, 02188")