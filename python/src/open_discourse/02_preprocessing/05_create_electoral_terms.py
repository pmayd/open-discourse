### imports ###

import logging

# import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.helper_functions.logging_config import setup_logger
from open_discourse.definitions.specific_functions.functions_step02_func_05_create_el_terms import (
    convert_electoral_term_dates,
    add_ids,
    save_as_csv,
    electoral_terms,
)

# logs
logger = setup_logger(__file__, logging.DEBUG)

logger.info("Script 02_05 starts")


save_as_csv(add_ids(convert_electoral_term_dates(electoral_terms)))


logger.info("Script 02_05 done.")


# To Do

# pytest
