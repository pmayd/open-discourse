# Standardbibliotheken
import logging

# Eigene Module
from open_discourse.helper_functions.logging_config import setup_logger
from open_discourse.specific_functions.functions_02_05 import convert_electoral_term_dates
from open_discourse.specific_functions.functions_02_05 import add_ids
from open_discourse.specific_functions.functions_02_05 import save_as_csv
from open_discourse.specific_functions.functions_02_05 import electoral_terms

# Logs
logger = setup_logger(__file__, logging.DEBUG)
logger.info("Script 02_05 starts")

# Script begin
converted_terms = convert_electoral_term_dates(electoral_terms)
terms_with_ids = add_ids(converted_terms)
save_as_csv(terms_with_ids)


logger.info("Script 02_05 done.")

# Script end
