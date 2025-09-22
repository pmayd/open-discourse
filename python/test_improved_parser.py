#!/usr/bin/env python3
"""Improved parser for handling session content extraction with interruptions."""

import xml.etree.ElementTree as et
from pathlib import Path
import regex
from typing import List, Tuple, Optional

# Improved patterns
BEGIN_PATTERN_IMPROVED = regex.compile(
    r"Die[^\.]*?Sitzung[^\.]*?wird[^\.]*?\d{1,2}[^\.]*?Uhr[^\.]*?(durch[^\.]*?den.*?)?(eröffnet|eingeleitet|wieder\s*aufgenommen)[^\.]*?[.]?",
    regex.V0 | regex.DOTALL
)

END_PATTERN_IMPROVED = regex.compile(
    r"\((?:Schluß|Schluss)[^)]*?Sitzung[^)]*?Uhr[^)]*?\)"
)

INTERRUPTION_PATTERN = regex.compile(
    r"\(Unterbrechung[^)]*?Sitzung[^)]*?\)",
    regex.V0 | regex.DOTALL
)

# Original patterns for comparison
ORIGINAL_BEGIN = regex.compile(
    r"Die.*?Sitzung.*?wird.*?\d{1,2}.*?Uhr.*?(durch.*?den.*?)?eröffnet"
)

ORIGINAL_END = regex.compile(r"\(Schluß.*?Sitzung.*?Uhr.*?\)")


def get_session_content_original(text_corpus: str) -> str:
    """Original function logic for comparison."""
    find_beginnings = list(ORIGINAL_BEGIN.finditer(text_corpus))
    find_endings = list(ORIGINAL_END.finditer(text_corpus))

    session_content = ""
    if len(find_beginnings) > len(find_endings) and len(find_endings) == 1:
        session_content = text_corpus[
            find_beginnings[0].span()[1] : find_endings[0].span()[0]
        ]
    elif len(find_beginnings) == len(find_endings):
        for begin, end in zip(find_beginnings, find_endings):
            session_content += text_corpus[begin.span()[1] : end.span()[0]]

    return session_content


def get_session_content_improved(text_corpus: str) -> str:
    """
    Improved extraction that handles interruptions and various session patterns.

    Strategy:
    1. Find all beginnings (including resumptions after interruptions)
    2. Find all endings
    3. Find all interruptions
    4. Extract content intelligently:
       - If there are interruptions, merge all segments
       - Otherwise use the original logic with improved patterns
    """
    find_beginnings = list(BEGIN_PATTERN_IMPROVED.finditer(text_corpus))
    find_endings = list(END_PATTERN_IMPROVED.finditer(text_corpus))
    find_interruptions = list(INTERRUPTION_PATTERN.finditer(text_corpus))

    session_content = ""

    # Debug info
    debug_info = {
        'beginnings': len(find_beginnings),
        'endings': len(find_endings),
        'interruptions': len(find_interruptions)
    }

    if not find_beginnings:
        return ""

    # Strategy 1: If there are interruptions, extract from first beginning to last ending
    if find_interruptions and find_endings:
        # Get the first real beginning (not a resumption)
        first_begin = find_beginnings[0]
        last_end = find_endings[-1]
        session_content = text_corpus[first_begin.span()[1] : last_end.span()[0]]

    # Strategy 2: More beginnings than endings with exactly one ending
    elif len(find_beginnings) > len(find_endings) and len(find_endings) == 1:
        session_content = text_corpus[
            find_beginnings[0].span()[1] : find_endings[0].span()[0]
        ]

    # Strategy 3: Equal beginnings and endings - pair them up
    elif len(find_beginnings) == len(find_endings) and find_endings:
        for begin, end in zip(find_beginnings, find_endings):
            session_content += text_corpus[begin.span()[1] : end.span()[0]]

    # Strategy 4: If we have beginnings but no proper ending, check for end of file
    elif find_beginnings and not find_endings:
        # Look for END OF FILE marker if it exists
        eof_pos = text_corpus.find("END OF FILE")
        if eof_pos > 0:
            session_content = text_corpus[find_beginnings[0].span()[1] : eof_pos]

    return session_content.strip(), debug_info


def test_specific_file(file_path: Path) -> dict:
    """Test both methods on a specific file."""
    try:
        tree = et.parse(file_path)
        text_elem = tree.find("TEXT")
        if text_elem is None or text_elem.text is None:
            return {'error': 'No TEXT element found'}

        text_corpus = text_elem.text
        # Add EOF marker as the original code does
        text_corpus += "\n\nEND OF FILE"

        # Test original method
        original_result = get_session_content_original(text_corpus)

        # Test improved method
        improved_result, debug_info = get_session_content_improved(text_corpus)

        return {
            'file': file_path.name,
            'original_length': len(original_result),
            'improved_length': len(improved_result),
            'original_found': len(original_result) > 0,
            'improved_found': len(improved_result) > 0,
            'debug': debug_info
        }
    except Exception as e:
        return {'error': str(e)}


def main():
    """Test the improved parser on problematic files."""

    # Problematic files from the issue
    problematic_files = {
        'electoral_term_pp01': [
            '01014.xml', '01001.xml', '01042.xml', '01280.xml',
            '01041.xml', '01281.xml', '01224.xml', '01019.xml',
            '01223.xml', '01183.xml'
        ],
        'electoral_term_pp02': [
            '02078.xml', '02188.xml'
        ]
    }

    xml_base = Path("./data/01_raw/xml")
    results = []

    print("Testing improved parser on problematic files...\n")
    print("=" * 70)

    for term_dir, files in problematic_files.items():
        term_path = xml_base / (term_dir + ".zip")
        if not term_path.exists():
            # Try without .zip extension
            term_path = xml_base / term_dir
            if not term_path.exists():
                print(f"Directory not found: {term_dir}")
                continue

        print(f"\nTerm: {term_dir}")
        print("-" * 40)

        for file_name in files:
            file_path = term_path / file_name
            if file_path.exists():
                result = test_specific_file(file_path)
                results.append(result)

                status_original = "✓" if result.get('original_found') else "✗"
                status_improved = "✓" if result.get('improved_found') else "✗"

                print(f"  {file_name:12} Original: {status_original}  Improved: {status_improved}")

                if result.get('debug'):
                    debug = result['debug']
                    print(f"               (B:{debug['beginnings']} E:{debug['endings']} I:{debug['interruptions']})")

                if result.get('improved_found') and not result.get('original_found'):
                    print(f"               → FIXED! Content found: {result['improved_length']} chars")
            else:
                print(f"  {file_name:12} File not found")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY:")

    fixed_count = sum(1 for r in results
                     if r.get('improved_found') and not r.get('original_found'))
    broken_count = sum(1 for r in results
                      if r.get('original_found') and not r.get('improved_found'))
    still_missing = sum(1 for r in results
                       if not r.get('improved_found') and not r.get('original_found'))

    print(f"Files fixed by improved parser: {fixed_count}")
    print(f"Files broken by improved parser: {broken_count}")
    print(f"Files still not extractable: {still_missing}")
    print(f"Total files tested: {len(results)}")


if __name__ == "__main__":
    main()