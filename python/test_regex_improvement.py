#!/usr/bin/env python3
"""Test script to compare old and new regex patterns for session beginnings."""

import regex
from pathlib import Path
import xml.etree.ElementTree as et

# Old pattern (current)
OLD_PATTERN = regex.compile(
    r"Die.*?Sitzung.*?wird.*?\d{1,2}.*?Uhr.*?(durch.*?den.*?)?eröffnet"
)

# New improved pattern (proposed)
NEW_PATTERN = regex.compile(
    r"Die[^\.]*?Sitzung[^\.]*?wird[^\.]*?\d{1,2}[^\.]*?Uhr[^\.]*?(durch[^\.]*?den.*?)?(eröffnet|eingeleitet)[^\.]*?[.]",
    regex.V0 | regex.DOTALL
)

def test_patterns():
    """Compare old and new patterns on XML files."""

    # Path to XML files
    xml_path = Path("./data/01_raw/xml")

    # Test specific problematic files mentioned in the issue
    test_files = ["02078.xml", "01014.xml", "01001.xml"]

    old_matches_total = 0
    new_matches_total = 0
    files_with_differences = []

    # Test all XML files in terms 1 and 2
    for term_dir in xml_path.iterdir():
        if not term_dir.is_dir():
            continue

        # Check if this is term 1 or 2
        if "01" not in term_dir.name and "02" not in term_dir.name:
            continue

        print(f"\nProcessing {term_dir.name}...")

        for xml_file in term_dir.glob("*.xml"):
            try:
                tree = et.parse(xml_file)
                text_corpus = tree.find("TEXT")
                if text_corpus is None or text_corpus.text is None:
                    continue

                text = text_corpus.text

                # Find matches with both patterns
                old_matches = list(OLD_PATTERN.finditer(text))
                new_matches = list(NEW_PATTERN.finditer(text))

                old_matches_total += len(old_matches)
                new_matches_total += len(new_matches)

                # Check if there's a difference
                if len(old_matches) != len(new_matches):
                    files_with_differences.append({
                        'file': xml_file.name,
                        'term': term_dir.name,
                        'old_count': len(old_matches),
                        'new_count': len(new_matches)
                    })

                    # Show details for specific test files
                    if xml_file.name in test_files:
                        print(f"\n  {xml_file.name}:")
                        print(f"    Old pattern found: {len(old_matches)} matches")
                        print(f"    New pattern found: {len(new_matches)} matches")

                        if len(new_matches) > 0 and len(old_matches) == 0:
                            match_text = text[new_matches[0].start():new_matches[0].end()]
                            # Clean up for display
                            match_text = ' '.join(match_text.split())[:100]
                            print(f"    New pattern matched: '{match_text}...'")

            except Exception as e:
                print(f"  Error processing {xml_file.name}: {e}")

    print("\n" + "="*60)
    print("SUMMARY:")
    print(f"Total matches with OLD pattern: {old_matches_total}")
    print(f"Total matches with NEW pattern: {new_matches_total}")
    print(f"Additional matches found: {new_matches_total - old_matches_total}")
    print(f"Files with differences: {len(files_with_differences)}")

    if files_with_differences:
        print("\nFiles where patterns differ:")
        for diff in files_with_differences[:10]:  # Show first 10
            print(f"  {diff['term']}/{diff['file']}: "
                  f"Old={diff['old_count']}, New={diff['new_count']}")

        if len(files_with_differences) > 10:
            print(f"  ... and {len(files_with_differences) - 10} more files")

if __name__ == "__main__":
    test_patterns()