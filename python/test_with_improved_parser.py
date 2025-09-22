#!/usr/bin/env python3
"""Test the preprocessing script with the improved parser."""

import xml.etree.ElementTree as et
from pathlib import Path
from tqdm import tqdm

# Import both parsers
from open_discourse.helper.parser import get_session_content as get_session_content_original
from open_discourse.helper.parser_improved import get_session_content as get_session_content_improved
from open_discourse.helper.clean_text import clean

# Problematic files identified in the log
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

RAW_XML = Path("./data/01_raw/xml")

print("Testing improved parser on problematic files from log")
print("=" * 70)

for term_folder in sorted(RAW_XML.iterdir()):
    if not term_folder.is_dir():
        continue

    term_name = term_folder.name.replace('.zip', '')

    if term_name not in problematic_files:
        continue

    print(f"\nProcessing {term_name}:")
    print("-" * 40)

    for file_name in problematic_files[term_name]:
        xml_file_path = term_folder / file_name

        if not xml_file_path.exists():
            print(f"  {file_name}: FILE NOT FOUND")
            continue

        try:
            tree = et.parse(xml_file_path)
            text_corpus = tree.find("TEXT").text

            # Clean text corpus (as done in original script)
            text_corpus = clean(text_corpus)

            # Append "END OF FILE" (as done in original script)
            text_corpus += "\n\nEND OF FILE"

            # Test with original parser
            original_content = get_session_content_original(text_corpus)

            # Test with improved parser
            improved_content = get_session_content_improved(text_corpus)

            original_status = "✓" if original_content else "✗"
            improved_status = "✓" if improved_content else "✗"

            status = f"Original: {original_status}  Improved: {improved_status}"

            if improved_content and not original_content:
                status += f" → FIXED! ({len(improved_content)} chars)"
            elif not improved_content and not original_content:
                status += " → Still broken"

            print(f"  {file_name}: {status}")

        except Exception as e:
            print(f"  {file_name}: ERROR - {e}")

print("\n" + "=" * 70)
print("Test complete!")