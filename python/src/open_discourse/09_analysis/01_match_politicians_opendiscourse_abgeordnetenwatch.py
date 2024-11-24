import datetime

import numpy as np
import pandas as pd
import requests
from sqlalchemy import create_engine

import open_discourse.definitions.path_definitions as path_definitions

engine = create_engine("postgresql://postgres:postgres@localhost:5432/next")

## Load Data
# Load Abgeordnetenwatch Data from API
all_data = []
page = 1
import time
while True:
    time.sleep(1)
    if page % 10 == 0:
        print(f"Page {page}")
    example = f"https://www.abgeordnetenwatch.de/api/v2/politicians?page={str(page)}"
    response = requests.get(example)
    r = response.json()
    last_count = int(r['meta']['result']['count'])
    all_data.extend(r['data'])
    if last_count == 0:
        break
    page += 1


df = pd.DataFrame(all_data)
df.shape

# filter for members of Bundestag
df_mbd = df.loc[df.ext_id_bundestagsverwaltung.notnull()]

# Load Open Discourse Data
PEOPLE = path_definitions.DATA_FINAL / "politicians.csv"
politicians = pd.read_csv(PEOPLE)
# remove duplicates by keeping first
politicians = politicians.drop_duplicates(subset=["ui", "first_name", "last_name"], keep="first")
politicians = politicians.drop_duplicates(subset=["ui"], keep="first")
politicians = politicians.drop(
    [
        "electoral_term",
        "faction_id",
        "institution_type",
        "institution_name",
        "constituency",
    ],
    axis=1,
)

politicians.columns = [
    "id",
    "first_name",
    "last_name",
    "birth_place",
    "birth_country",
    "birth_date",
    "death_date",
    "gender",
    "profession",
    "aristocracy",
    "academic_title",
]
print(f"We have {df_mbd.shape[0]} members of Bundestag in the Abgeordnetenwatch API and {politicians.shape[0]} MdB in the Open Discourse data.")
print(f"The discrepancy is due to the fact that Abgeordnetenwatch started collecting data in the 2000s, while Open Discourse has a complete dataset from Bundestagsverwaltung.")

## Prep data
df_mbd['year_of_birth'] = df_mbd['year_of_birth'].fillna("-1")
df_mbd['year_of_birth'] = df_mbd['year_of_birth'].apply(lambda x: str(int(x)) if x != "-1" else x)
politicians['year_of_birth'] = politicians['birth_date'].apply(lambda x: str(pd.to_datetime(x, format='mixed').year) if x != "-1" else x)
# remove capitalization and replace - with space for first and last names in both datasets
for col in ["first_name", "last_name"]:
    df_mbd[col] = df_mbd[col].str.strip().str.lower().str.replace("-", " ")
    politicians[col] = politicians[col].str.strip().str.lower().str.replace("-", " ")


# since df_mbd is the smalller dataset, we match onto this one
# start with exact match via left join on first name, last name and birth year
merge_cols = ["first_name", "last_name", "year_of_birth"]
exact_matches_unique = df_mbd.merge(politicians, how='left', left_on=merge_cols, right_on=['first_name', 'last_name', 'year_of_birth'], suffixes=('_aw', '_od')).drop_duplicates("id_aw", keep=False).dropna(subset=['id_od'])
df_mdb_left = df_mbd.loc[~df_mbd.id.isin(exact_matches_unique.id_aw)]
politicians_left = politicians.loc[~politicians.id.isin(exact_matches_unique.id_od)]
print(f"Of {df_mbd.shape[0]} politicians in the Abgeordnetenwatch API, {exact_matches_unique.shape[0]} could be matched exactly on {str(merge_cols)}, and {df_mdb_left.shape[0]} are left to be matched.")

import pandas as pd
from fuzzywuzzy import fuzz
from typing import List
def fuzzy_match_cols(df1: pd.DataFrame, df2: pd.DataFrame, id_cols: List[str], match_cols: List[str], weights=None, threshold=80) -> pd.DataFrame:
    """
    Match names between two dataframes using fuzzy string matching.

    Parameters:
    -----------
    df1, df2 : pandas.DataFrame
        DataFrames containing the names to match
    fname_col1, fname_col2 : str
        Column names for first names in df1 and df2
    lname_col1, lname_col2 : str
        Column names for last names in df1 and df2
    threshold : int
        Minimum match score (0-100) to consider a match

    Returns:
    --------
    pandas.DataFrame
        DataFrame with matched names and their scores
    """
    weights = len(match_cols) * [1] if weights is None else weights
    # Clean names: lowercase and strip whitespace
    for df in [df1, df2]:
        for col in match_cols:
            if col in df.columns:
                df[col] = df[col].str.strip()

    matches = []

    # Create all possible pairs of names
    for _, row1 in df1.iterrows():
        for _, row2 in df2.iterrows():
            match_scores = []
            for col, weight in zip(match_cols, weights):
                match_scores.append(fuzz.ratio(str(row1[col]), str(row2[col])) * weight)

            # Calculate overall match score
            match_score = sum(match_scores) / sum(weights)

            # If score exceeds threshold, add to matches
            if match_score >= threshold:
                data = {
                    'df1_index': row1[id_cols[0]],
                    'df2_index': row2[id_cols[1]],
                    'overall_score': match_score
                }
                for col in match_cols:
                    data[f"df1_{col}"] = row1[col]
                    data[f"df2_{col}"] = row2[col]
                matches.append(data)

    # Convert matches to DataFrame and sort by score
    matches_df = pd.DataFrame(matches).sort_values('overall_score', ascending=False)

    return matches_df

# Find matches
matches = fuzzy_match_cols(df_mdb_left, politicians_left,id_cols=["id", "id"] , match_cols=["first_name", "last_name"], threshold=50)
matches["df1_year_of_birth"] = matches["df1_index"].map(df_mdb_left.set_index("id")["year_of_birth"])
matches["df2_year_of_birth"] = matches["df2_index"].map(politicians_left.set_index("id")["year_of_birth"])
# highest_matches = matches.drop_duplicates(subset=["df1_index"], keep="first")
highest_matches_w_matching_birthyear_over_70 = matches.loc[(matches.df1_year_of_birth == matches.df2_year_of_birth) & (matches.df1_year_of_birth != "-1") & (matches.overall_score > 70)].drop_duplicates(subset=["df1_index"], keep="first")
rest = matches.loc[~matches.df1_index.isin(highest_matches_w_matching_birthyear_over_70.df1_index)]
# remove non-matching birth years except where birth year is -1
# these need to be matched manually
rest = rest.loc[(rest.df1_year_of_birth == rest.df2_year_of_birth) | (rest.df1_year_of_birth == "-1")].drop_duplicates(subset=["df1_index"], keep="first")

