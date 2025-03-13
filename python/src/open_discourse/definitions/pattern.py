import regex

FACTIONS = {
    "Bündnis 90/Die Grünen": regex.compile(
        "(?:BÜNDNIS\s*(?:90)?/?(?:\s*D[1I]E)?|Bündnis\s*90/(?:\s*D[1I]E)?)?\s*[GC]R[UÜ].?\s*[ÑN]EN?(?:/Bündnis 90)?|Bündnis 90/Die Grünen"
    ),
    "CDU/CSU": regex.compile(
        "(?:Gast|-)?(?:\s*C\s*[DSMU]\s*S?[DU]\s*(?:\s*[/,':!.-]?)*\s*(?:\s*C+\s*[DSs]?\s*[UÙ]?\s*)?)(?:-?Hosp\.|-Gast|1)?"
    ),
    "BP": regex.compile("^BP"),
    "DA": regex.compile("^DA"),
    "DP": regex.compile("^DP"),
    "DIE LINKE.": regex.compile("DIE LINKE"),
    "DPB": regex.compile("(?:^DPB)"),
    "DRP": regex.compile("DRP(\-Hosp\.)?|SRP"),
    "FDP": regex.compile("\s*F\.?\s*[PDO][.']?[DP]\.?"),
    "Fraktionslos": regex.compile("(?:fraktionslos|Parteilos|parteilos)"),
    "FU": regex.compile("^FU"),
    "FVP": regex.compile("^FVP"),
    "Gast": regex.compile("Gast"),
    "GB/BHE": regex.compile("(?:GB[/-]\s*)?BHE(?:-DG)?"),
    "KPD": regex.compile("^KPD"),
    "PDS": regex.compile("(?:Gruppe\s*der\s*)?PDS(?:/(?:LL|Linke Liste))?"),
    "SPD": regex.compile("\s*'?S(?:PD|DP)(?:\.|-Gast)?"),
    "SSW": regex.compile("^SSW"),
    "SRP": regex.compile("^SRP"),
    "WAV": regex.compile("^WAV"),
    "Z": regex.compile("^Z$"),
    "DBP": regex.compile("^DBP$"),
    "NR": regex.compile("^NR$"),
}
