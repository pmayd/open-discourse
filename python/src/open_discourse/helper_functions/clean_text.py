import re

import numpy as np


def clean(filetext: str, remove_pdf_header: bool = True) -> str:
    # Replaces all the misrecognized characters
    filetext = filetext.replace(r"", "-")
    filetext = filetext.replace(r"", "-")
    filetext = filetext.replace("—", "-")
    filetext = filetext.replace("–", "-")
    filetext = filetext.replace("•", "")
    filetext = re.sub(r"\t+", " ", filetext)
    filetext = re.sub(r"  +", " ", filetext)

    # Remove pdf artifact
    if remove_pdf_header:
        filetext = re.sub(
            r"(?:Deutscher\s?Bundestag\s?-(?:\s?\d{1,2}\s?[,.]\s?Wahlperiode\s?-)?)?\s?\d{1,3}\s?[,.]\s?Sitzung\s?[,.]\s?(?:(?:Bonn|Berlin)[,.])?\s?[^,.]+,\s?den\s?\d{1,2}\s?[,.]\s?[^\d]+\d{4}.*",
            r"\n",
            filetext,
        )
        filetext = re.sub(r"\s*(\(A\)|\(B\)|\(C\)|\(D\))", "", filetext)

    # Remove delimeter
    filetext = re.sub(r"-\n+(?![^(]*\))", "", filetext)

    filetext = remove_newlines_in_brackets(filetext)

    return filetext


def remove_newlines_in_brackets(filetext: str) -> str:
    # Finds all text within parentheses, including nested parentheses
    bracket_text = re.findall(r"\(([^(\)]*(\(([^(\)]*)\))*[^(\)]*)\)", filetext)

    for sub_groups in bracket_text:
        bracket_content = sub_groups[0]
        bracket_content = re.sub(
            r"(^((?<!Abg\.).)+|^.*\[.+)(-\n+)",
            r"\1",
            bracket_content,
            flags=re.MULTILINE,
        )
        bracket_content = re.sub(r"\n+", " ", bracket_content)
        filetext = filetext.replace(sub_groups[0], bracket_content)

    return filetext


def clean_name_headers(
    filetext: str, names: list[str], contributions_extended_filter: bool = False
):
    """Cleans lines a given text which remained from the pdf header.
    Usually something like: "Präsident Dr. Lammert"
    Keep in mind this also deletes lines from voting lists.
    """
    if contributions_extended_filter:
        table = {ord(c): "" for c in "()[]{}"}
        names = np.unique([name.translate(table) for name in names])

    table = {ord("+"): "\\+", ord("*"): "\\*", ord("?"): "\\?"}
    names_to_clean = ("(" + "|".join(names) + ")").translate(table)
    pattern = (
        r"\n((?:Parl\s?\.\s)?Staatssekretär(?:in)?|Bundeskanzler(?:in)?|Bundesminister(?:in)?|Staatsminister(:?in)?)?\s?"
        + names_to_clean
        + r" *\n"
    )
    filetext = re.sub(pattern, "\n", filetext)

    pattern = r"\n\d+ *\n"

    filetext = re.sub(pattern, "\n", filetext)

    return filetext
