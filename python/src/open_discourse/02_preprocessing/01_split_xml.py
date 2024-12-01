import logging

import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.helper_functions.functions_step02_func_01_split_xml import (
    pp_iterate_03_to_19,
)
from open_discourse.helper_functions.logging_config import setup_logger

logger = setup_logger(__file__, logging.DEBUG)
logger.info("Script 02_01 starts")

# input directory
RAW_XML = path_definitions.RAW_XML

# output directory
RAW_TXT = path_definitions.RAW_TXT
RAW_TXT.mkdir(parents=True, exist_ok=True)

# iterate through entire data or select one term or one session
# pp_iterate_03_to_19(RAW_XML, RAW_TXT, 4, session=19)
pp_iterate_03_to_19(RAW_XML, RAW_TXT)

logger.info("Script 02_01 ends")
