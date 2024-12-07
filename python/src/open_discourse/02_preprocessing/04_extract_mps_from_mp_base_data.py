import xml.etree.ElementTree as et

import pandas as pd
import regex

import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.specific_functions.process_single_mdb import process_single_mdb

# input directory
MP_BASE_DATA = path_definitions.MP_BASE_DATA

# output directory
POLITICIANS_STAGE_01 = path_definitions.POLITICIANS_STAGE_01
POLITICIANS_STAGE_01.mkdir(parents=True, exist_ok=True)
save_path = POLITICIANS_STAGE_01 / "mps.pkl"

print("Process mps...", end="", flush=True)
# read data
tree = et.parse(MP_BASE_DATA)
root = tree.getroot()


# last_names_to_revisit = []
# i = 0
# Iterate over all MDBs (Mitglieder des Bundestages) in XML File.
mp_data = []
df = pd.DataFrame()
for mdb in tree.iter("MDB"):
    #print("\nBDC",type(mdb),mdb)
    mp_data = process_single_mdb(mdb)
    df = pd.concat([df, pd.DataFrame([mp_data])], ignore_index=True)
    #mp_data.append(process_single_mdb(mdb))
    # break

df = pd.DataFrame(mp_data)
df["constituency"] = df["constituency"].str.replace("[)(]", "", regex=True)
df = df.astype(dtype={"ui": "int64", "birth_date": "str", "death_date": "str"})

print(df.info())
print(df)
df.to_pickle(save_path)

print("Script 02_04 done.")
