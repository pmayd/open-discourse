# import pandas as pl
# from sqlalchemy import create_engine
import numpy as np
import datetime
from transformers import pipeline
import open_discourse.definitions.path_definitions as path_definitions
import pandas as pd
# engine = create_engine("postgresql://postgres:postgres@localhost:5432/next")

# Load Final Data

CONTRIBUTIONS_EXTENDED = path_definitions.DATA_FINAL / "contributions_extended.pkl"
SPOKEN_CONTENT = path_definitions.DATA_FINAL / "speech_content.pkl"
FACTIONS = path_definitions.DATA_FINAL / "factions.pkl"
PEOPLE = path_definitions.DATA_FINAL / "politicians.csv"
CONTRIBUTIONS_SIMPLIFIED = (
    path_definitions.CONTRIBUTIONS_SIMPLIFIED / "contributions_simplified.pkl"
)
CONTRIBUTIONS_SIMPLIFIED_WP20 = (
    path_definitions.CONTRIBUTIONS_SIMPLIFIED
    / "electoral_term_pp20"
    / "contributions_simplified.pkl"
)
ELECTORAL_TERMS = path_definitions.ELECTORAL_TERMS / "electoral_terms.csv"

# Load data
electoral_terms = pd.read_csv(ELECTORAL_TERMS)
politicians = pd.read_csv(PEOPLE)
politicians = politicians.drop_duplicates(keep="last", subset=["ui"])
speeches = pd.read_pickle(SPOKEN_CONTENT)
contributions_extended = pd.read_pickle(CONTRIBUTIONS_EXTENDED)
contributions_simplified = pd.read_pickle(CONTRIBUTIONS_SIMPLIFIED)
contributions_simplified_electoral_term_20 = pd.read_pickle(
    CONTRIBUTIONS_SIMPLIFIED_WP20
)

contributions_simplified = pd.concat(
    [
        contributions_simplified,
        contributions_simplified_electoral_term_20,
    ],
    sort=False,
)

contributions_simplified = contributions_simplified.where(
    (pd.notnull(contributions_simplified)), None
)

contributions_simplified["id"] = range(len(contributions_simplified.content))

# spoken content
spoken_content = pd.read_pickle(SPOKEN_CONTENT)
spoken_content20 = spoken_content[spoken_content["electoral_term"] == 20]


spoken_content20.speech_content.apply(lambda x: len(x)).value_counts()
speeches_over_2k = spoken_content20[
    spoken_content20.speech_content.apply(lambda x: len(x)) > 2000
]
speeches_over_2k
speech_index = 60
speech = speeches_over_2k.speech_content.iloc[speech_index]
print(speech)
# remove pattern ({number})
import re

pattern = r"\({(\d+)}\)"
speech = re.sub(pattern, "", speech)
speech = re.sub(r"\s+", " ", speech)
pipeline_classification_topics = pipeline(
    "text-classification", model="chkla/parlbert-topic-german", top_k=5
)
overlap = 128
# text = "Das Sachgebiet Investive Ausgaben des Bundes Bundesfinanzminister Apel hat gemäß BMF Finanznachrichten vom 1. Januar erklärt, die Investitionsquote des Bundes sei in den letzten zehn Jahren nahezu konstant geblieben."
for n in range(0, len(speech), 512 - overlap):
    # text = speech[n * (512 - overlap) : (n + 1) * (512 - overlap)]
    text = speech[n : n + 512]
    print("-------------------")
    print(pipeline_classification_topics(text))  # Macroeconomics
    print(text)
    print("-------------------")
# contributions_simplified.to_sql(
#     engine,
#     "contributions_simplified",
#     if_exists="append",
#     schema="open_discourse",
#     index=False,
# )
# print("Done.")
