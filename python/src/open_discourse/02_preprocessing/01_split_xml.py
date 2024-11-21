import logging

from open_discourse.helper_functions.logging_config import setup_logger
import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.helper_functions.functions_step02_func_01_split_xml import pp_iterate_03_to_19

logger = setup_logger('01_split.log', logging.DEBUG)
logger.debug(f"Script 02_01 starts")

# input directory
RAW_XML = path_definitions.RAW_XML

# output directory
RAW_TXT = path_definitions.RAW_TXT
RAW_TXT.mkdir(parents=True, exist_ok=True)

# iterate through entire data or select one term or one session
# pp_iterate_03_to_19(RAW_XML, RAW_TXT, 4, session=19)
pp_iterate_03_to_19(RAW_XML, RAW_TXT)

logger.debug(f"Script 02_01 ends")
