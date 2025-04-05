"""
Constants used across the Open Discourse project.

This module provides centralized access to constants used by various parts of the
Open Discourse pipeline, including factions processing and politicians processing.
"""

# Constants for the factions processing
ADDITIONAL_FACTIONS = [
    "Südschleswigscher Wählerverband",  # A regional party in Germany
    "Gast",  # Represents guest speakers or members
    "Gruppe Nationale Rechte",  # A group with national right-wing affiliations
    "Deutsche Soziale Union",  # A social union in Germany
]

# Constants for the politicians processing
ELECTORAL_TERMS = {
    "from": [
        1949,
        1953,
        1957,
        1961,
        1965,
        1969,
        1972,
        1976,
        1980,
        1983,
        1987,
        1990,
        1994,
        1998,
        2002,
        2005,
        2009,
        2013,
        2017,
    ],
    "until": [
        1953,
        1957,
        1961,
        1965,
        1969,
        1972,
        1976,
        1980,
        1983,
        1987,
        1990,
        1994,
        1998,
        2002,
        2005,
        2009,
        2013,
        2017,
        -1,
    ],
}

# Regex patterns for matching faction names
FACTION_PATTERNS = {
    "Bündnis 90/Die Grünen": r"(?:BÜNDNIS\s*(?:90)?/?(?:\s*D[1I]E)?|Bündnis\s*90/(?:\s*D[1I]E)?)?\s*[GC]R[UÜ].?\s*[ÑN]EN?(?:/Bündnis 90)?|Bündnis 90/Die Grünen",
    "CDU/CSU": r"(?:Gast|-)?(?:\s*C\s*[DSMU]\s*S?[DU]\s*(?:\s*[/,':!.-]?)*\s*(?:\s*C+\s*[DSs]?\s*[UÙ]?\s*)?)(?:-?Hosp\.|-Gast|1)?",
    "BP": r"^BP",
    "DA": r"^DA",
    "DP": r"^DP",
    "DIE LINKE.": r"DIE LINKE",
    "DPB": r"(?:^DPB)",
    "DRP": r"DRP(\-Hosp\.)?|SRP",
    "DSU": r"^DSU",
    "FDP": r"\s*F\.?\s*[PDO][.']?[DP]\.?",
    "Fraktionslos": r"(?:fraktionslos|Parteilos|parteilos)",
    "FU": r"^FU",
    "FVP": r"^FVP",
    "Gast": r"Gast",
    "GB/BHE": r"(?:GB[/-]\s*)?BHE(?:-DG)?",
    "KPD": r"^KPD",
    "PDS": r"(?:Gruppe\s*der\s*)?PDS(?:/(?:LL|Linke Liste))?",
    "SPD": r"\s*'?S(?:PD|DP)(?:\.|-Gast)?",
    "SSW": r"^SSW",
    "SRP": r"^SRP",
    "WAV": r"^WAV",
    "Z": r"^Z$",
    "DBP": r"^DBP$",
    "NR": r"^NR$",
}

# Dictionary mapping full faction names to their abbreviations
FACTION_ABBREVIATIONS = {
    "Alternative für Deutschland": "AfD",
    "Deutsche Soziale Union": "DSU",
    "Fraktion Alternative für Deutschland": "AfD",
    "Fraktion Bayernpartei": "BP",
    "Fraktion Bündnis 90/Die Grünen": "Bündnis 90/Die Grünen",
    "Fraktion DIE LINKE.": "DIE LINKE.",
    "Fraktion DP/DPB (Gast)": "DP/DPB",
    "Fraktion DRP (Gast)": "DRP",
    "Fraktion Demokratische Arbeitsgemeinschaft": "DA",
    "Fraktion Deutsche Partei": "DP",
    "Fraktion Deutsche Partei Bayern": "DPB",
    "Fraktion Deutsche Partei/Deutsche Partei Bayern": "DP/DPB",
    "Fraktion Deutsche Partei/Freie Volkspartei": "DP/FVP",
    "Fraktion Deutsche Reichspartei": "DRP",
    "Fraktion Deutsche Reichspartei/Nationale Rechte": "DRP/NR",
    "Fraktion Deutsche Zentrums-Partei": "Z",
    "Fraktion Deutscher Gemeinschaftsblock der Heimatvertriebenen und Entrechteten": "BHE",
    "Fraktion Die Grünen": "Bündnis 90/Die Grünen",
    "Fraktion Die Grünen/Bündnis 90": "Bündnis 90/Die Grünen",
    "Fraktion BÜNDNIS 90/DIE GRÜNEN": "Bündnis 90/Die Grünen",
    "Fraktion Freie Volkspartei": "FVP",
    "Fraktion Föderalistische Union": "FU",
    "Fraktion Gesamtdeutscher Block / Block der Heimatvertriebenen und Entrechteten": "GB/BHE",
    "Fraktion WAV (Gast)": "WAV",
    "Fraktion Wirtschaftliche Aufbauvereinigung": "WAV",
    "Fraktion der CDU/CSU (Gast)": "CDU/CSU",
    "Fraktion der Christlich Demokratischen Union/Christlich - Sozialen Union": "CDU/CSU",
    "Fraktion der FDP (Gast)": "FDP",
    "Fraktion der Freien Demokratischen Partei": "FDP",
    "Fraktion der Kommunistischen Partei Deutschlands": "KPD",
    "Fraktion der Partei des Demokratischen Sozialismus": "PDS",
    "Fraktion der SPD (Gast)": "SPD",
    "Fraktion der Sozialdemokratischen Partei Deutschlands": "SPD",
    "Fraktionslos": "Fraktionslos",
    "Gruppe Bündnis 90/Die Grünen": "Bündnis 90/Die Grünen",
    "Gruppe BSW - Bündnis Sahra Wagenknecht - Vernunft und Gerechtigkeit": "BSW",
    "Gruppe Deutsche Partei": "DP",
    "Gruppe Die Linke": "DIE LINKE.",
    "Gruppe Kraft/Oberländer": "KO",
    "Gruppe der Partei des Demokratischen Sozialismus": "PDS",
    "Gruppe der Partei des Demokratischen Sozialismus/Linke Liste": "PDS",
    "Südschleswigscher Wählerverband": "SSW",
    "Gast": "Gast",
    "Gruppe Nationale Rechte": "NR",
}
