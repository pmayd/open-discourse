"""
Iterate through entire data or select one term or one session
"""

import logging

import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.helper_functions.logging_config import setup_and_get_logger
from open_discourse.specific_functions.func_step02_func01 import (
    iterate_preprocessing_completed_terms,
)

logger = setup_and_get_logger(__file__, logging.DEBUG)
logger.info("Script 02_01 starts")

# input directory
RAW_XML = path_definitions.RAW_XML

# output directory
RAW_TXT = path_definitions.RAW_TXT
RAW_TXT.mkdir(parents=True, exist_ok=True)

# iterate through entire data or select one term or one session
# iterate_preprocessing_completed_terms(RAW_XML, RAW_TXT, 4, session=19)
iterate_preprocessing_completed_terms(RAW_XML, RAW_TXT)

logger.info("Script 02_01 ends")
