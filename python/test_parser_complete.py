#!/usr/bin/env python3
"""
Complete test suite for the session parser fix.
This script provides detailed, step-by-step verification of the improvements.

Run this to verify that the parser fix is working correctly.
"""

import xml.etree.ElementTree as et
from pathlib import Path
import regex
from typing import List, Tuple
from open_discourse.helper.clean_text import clean

# Terminal colors for better readability
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")

def print_section(text: str):
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.CYAN}{'-'*40}{Colors.RESET}")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_failure(text: str):
    """Print failure message."""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.YELLOW}ℹ️  {text}{Colors.RESET}")

def test_regex_patterns():
    """Test the regex patterns with sample text."""
    print_section("Testing Regex Patterns")

    # Test cases
    test_cases = [
        {
            'name': 'Standard opening',
            'text': 'Die Sitzung wird um 16 Uhr durch den Präsidenten eröffnet.',
            'should_match': True
        },
        {
            'name': 'Opening with newline',
            'text': 'Die Sitzung wird um 16 Uhr durch\nden Präsidenten eröffnet.',
            'should_match': True
        },
        {
            'name': 'Alternative word: eingeleitet',
            'text': 'Die Sitzung wird um 16 Uhr 5 Minuten eingeleitet mit der Ouvertüre',
            'should_match': True
        },
        {
            'name': 'Session resumption',
            'text': 'Die Sitzung wird um 19 Uhr 8 Minuten wieder aufgenommen.',
            'should_match': True
        }
    ]

    # Old pattern (fails with newlines and alternatives)
    old_pattern = regex.compile(
        r"Die.*?Sitzung.*?wird.*?\d{1,2}.*?Uhr.*?(durch.*?den.*?)?eröffnet"
    )

    # New improved pattern
    new_pattern = regex.compile(
        r"Die[^\.]*?Sitzung[^\.]*?wird[^\.]*?\d{1,2}[^\.]*?Uhr[^\.]*?"
        r"(durch[^\.]*?den.*?)?(eröffnet|eingeleitet|wieder\s*aufgenommen)[^\.]*?[.]?",
        regex.V0 | regex.DOTALL
    )

    for case in test_cases:
        print(f"\n  Testing: {case['name']}")
        print(f"  Text: '{case['text'][:50]}...'")

        old_match = old_pattern.search(case['text'])
        new_match = new_pattern.search(case['text'])

        old_status = "✓" if old_match else "✗"
        new_status = "✓" if new_match else "✗"

        print(f"    Old pattern: {old_status}")
        print(f"    New pattern: {new_status}")

        if new_match and not old_match and case['should_match']:
            print_success(f"  Fixed by new pattern!")
        elif not new_match and case['should_match']:
            print_failure(f"  Still not working!")

def analyze_problematic_files():
    """Analyze the problematic files in detail."""
    print_section("Analyzing Problematic Files")

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
    total_fixed = 0
    total_failed = 0
    details = []

    for term_name, files in problematic_files.items():
        term_path = xml_base / (term_name + ".zip")
        if not term_path.exists():
            term_path = xml_base / term_name

        if not term_path.exists():
            print_failure(f"Directory not found: {term_name}")
            continue

        print(f"\n  {Colors.BOLD}Period {term_name[-1]}:{Colors.RESET}")

        for file_name in files:
            file_path = term_path / file_name
            if not file_path.exists():
                print_failure(f"    {file_name}: File not found")
                continue

            try:
                tree = et.parse(file_path)
                text_elem = tree.find("TEXT")
                if text_elem is None or text_elem.text is None:
                    print_failure(f"    {file_name}: No TEXT element")
                    continue

                text = clean(text_elem.text) + "\n\nEND OF FILE"

                # Import the actual parser functions
                from open_discourse.helper.parser import get_session_content

                # Test with the improved parser
                result = get_session_content(text)

                if result:
                    print_success(f"    {file_name}: Extracts {len(result):,} chars")
                    total_fixed += 1
                    details.append({
                        'file': file_name,
                        'term': term_name[-1],
                        'size': len(result)
                    })
                else:
                    print_failure(f"    {file_name}: Still fails")
                    total_failed += 1

            except Exception as e:
                print_failure(f"    {file_name}: Error - {e}")
                total_failed += 1

    return total_fixed, total_failed, details

def run_comprehensive_test():
    """Run the complete test suite."""
    print_header("COMPREHENSIVE PARSER FIX TEST SUITE")

    # Step 1: Test regex patterns
    test_regex_patterns()

    # Step 2: Analyze problematic files
    print("\n")
    total_fixed, total_failed, details = analyze_problematic_files()

    # Step 3: Summary
    print_header("TEST RESULTS SUMMARY")

    if total_fixed == 12 and total_failed == 0:
        print_success(f"ALL {total_fixed} FILES SUCCESSFULLY FIXED!")
        print(f"\n{Colors.GREEN}The parser improvements are working perfectly!{Colors.RESET}")
    else:
        print(f"\nFiles fixed: {Colors.GREEN}{total_fixed}{Colors.RESET}")
        print(f"Files still failing: {Colors.RED}{total_failed}{Colors.RESET}")

    # Calculate total data recovered
    total_chars = sum(d['size'] for d in details)
    print(f"\n{Colors.BOLD}Total data recovered:{Colors.RESET} {total_chars:,} characters (~{total_chars/1_000_000:.1f} MB)")

    # Show detailed breakdown
    print_section("Detailed Breakdown by File")
    print(f"\n{'File':<15} {'Period':<8} {'Characters':<15} {'Size (KB)':<10}")
    print("-" * 50)
    for d in sorted(details, key=lambda x: x['size'], reverse=True):
        size_kb = d['size'] / 1024
        print(f"{d['file']:<15} {d['term']:<8} {d['size']:>12,}   {size_kb:>8.1f}")

    # Instructions for next steps
    print_header("NEXT STEPS")
    print("\n1. If all tests pass (12 files fixed), the solution is ready")
    print("2. Run the actual preprocessing script:")
    print(f"   {Colors.CYAN}venv/bin/python src/open_discourse/steps/preprocessing/split_xml_electoral_term_1_and_2.py{Colors.RESET}")
    print("3. Verify no 'No session content found' errors appear in the log")
    print("4. Commit the changes to the branch")

if __name__ == "__main__":
    run_comprehensive_test()