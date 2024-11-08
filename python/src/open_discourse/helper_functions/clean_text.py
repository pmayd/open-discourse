import numpy as np
import regex


def clean(filetext, remove_pdf_header=True):
    # Replaces all the misrecognized characters
    filetext = filetext.replace(r"", "-")
    filetext = filetext.replace(r"", "-")
    filetext = filetext.replace("—", "-")
    filetext = filetext.replace("–", "-")
    filetext = filetext.replace("•", "")
    filetext = regex.sub(r"\t+", " ", filetext)
    filetext = regex.sub(r"  +", " ", filetext)

    # Remove pdf artifact
    if remove_pdf_header:
        filetext = regex.sub(
            r"(?:Deutscher\s?Bundestag\s?-(?:\s?\d{1,2}\s?[,.]\s?Wahlperiode\s?-)?)?\s?\d{1,3}\s?[,.]\s?Sitzung\s?[,.]\s?(?:(?:Bonn|Berlin)[,.])?\s?[^,.]+,\s?den\s?\d{1,2}\s?[,.]\s?[^\d]+\d{4}.*",
            r"\n",
            filetext,
        )
        filetext = regex.sub(r"\s*(\(A\)|\(B\)|\(C\)|\(D\))", "", filetext)

    # Remove delimeter
    filetext = regex.sub(r"-\n+(?![^(]*\))", "", filetext)

    # Deletes all the newlines in brackets
    bracket_text = regex.finditer(r"\(([^(\)]*(\(([^(\)]*)\))*[^(\)]*)\)", filetext)

    for bracket in bracket_text:
        filetext = filetext.replace(
            str(bracket.group()),
            regex.sub(
                r"\n+",
                " ",
                regex.sub(
                    r"(^((?<!Abg\.).)+|^.*\[.+)(-\n+)",
                    r"\1",
                    str(bracket.group()),
                    flags=regex.MULTILINE,
                ),
            ),
        )
    return filetext


def clean_name_headers(filetext, names, contributions_extended_filter=False):
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
    filetext = regex.sub(pattern, "\n", filetext)

    pattern = r"\n\d+ *\n"

    filetext = regex.sub(pattern, "\n", filetext)

    return filetext
