import logging
import xml.etree.ElementTree as Et

import pandas as pd

import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.helper_functions.logging_config import setup_logger
from open_discourse.specific_functions.func_step02_func04_extract_mps import (
    process_single_mdb,
)

logger = setup_logger(__file__, logging.DEBUG)
logger.info("Script 02_04 start: Process mps...")

# input directory
MP_BASE_DATA = path_definitions.MP_BASE_DATA
# output directory
POLITICIANS_STAGE_01 = path_definitions.POLITICIANS_STAGE_01
POLITICIANS_STAGE_01.mkdir(parents=True, exist_ok=True)
save_path = POLITICIANS_STAGE_01 / "mps.pkl"

# read data
tree = Et.parse(MP_BASE_DATA)
root = tree.getroot()


# Iterate over all MDBs (Mitglieder des Bundestages) in XML File.
mp_data = []
df = pd.DataFrame()
for mdb in tree.iter("MDB"):
    mp_data = process_single_mdb(mdb)
    df_tmp = pd.DataFrame(mp_data)
    df = pd.concat([df, df_tmp], ignore_index=True)

df["constituency"] = df["constituency"].str.replace("[)(]", "", regex=True)
df = df.astype(dtype={"ui": "int64", "birth_date": "str", "death_date": "str"})

df.to_pickle(save_path)

logger.info("Script 02_04 done.")
