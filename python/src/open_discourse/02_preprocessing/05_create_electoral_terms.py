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

# Script begin
converted_terms = convert_electoral_term_dates(electoral_terms)
terms_with_ids = add_ids(converted_terms)
save_as_csv(terms_with_ids)


logger.info("Script 02_05 done.")

# script end


# - - -
# To Do
# - - - - -
# pytest
