"""
Iterate through entire data or select one term or one session
"""

import logging
from pathlib import Path

import pandas as pd

import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.helper_functions.logging_config import setup_and_get_logger
from open_discourse.standalone_data_checks.functions_special_char import (
    get_stopword_dict, count_special_chars, yield_xml_file_iterator,
)

logger = setup_and_get_logger(__file__, logging.INFO)
logger.info("Script analyze_special_chars starts")

# input directory
RAW_XML = path_definitions.RAW_XML


df = pd.DataFrame()

# iterate through entire data or select one term or one session
for metadata,text_corpus in yield_xml_file_iterator(RAW_XML,4,19):
# for metadata, text_corpus in yield_xml_file_iterator():
    #print(metadata["document_number"])

    # df with one row and n columns for one session protocol
    df = pd.concat([df,count_special_chars(metadata["document_number"], text_corpus)])


# Sort df columns
col = sorted(df.columns[1:])
col = list(df.columns[:1]) +col
df = df[col]

# Replace NaN and recast
num_cols = df.select_dtypes(include=["number"]).columns
df[num_cols] = df[num_cols].fillna(0).astype('int32')
print(df.info(),df)



output_path = path_definitions.DATA_CACHE / "standalone_data_checks"
output_path.mkdir(parents=False, exist_ok=True)
file_path = Path(output_path,"df_special_char.p")
print("DED",file_path)
df.to_pickle(file_path)

logger.info("Script analyze_special_chars ends")