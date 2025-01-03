# see https://blog.mathieu-leplatre.info/tips-for-your-makefile-with-python.html
NAME := open_discourse
VENV := $(shell echo $${VIRTUAL_ENV-.venv})
UV := $(shell command -v uv 2> /dev/null)
PYTHON := $(VENV)/bin/python
INSTALL_STAMP := $(VENV)/.install.stamp
INSTALL_DEV_STAMP := $(VENV)/.install.dev.stamp

.DEFAULT_GOAL = install-dev

$(PYTHON):
	@if [ -z $(UV) ]; then echo "uv could not be found."; exit 2; fi
	$(UV) venv $(VENV)

.PHONY: install
install: $(INSTALL_STAMP)

$(INSTALL_STAMP): $(PYTHON) pyproject.toml
	$(UV) sync --no-dev
	touch $(INSTALL_STAMP)

.PHONY: install-dev
install-dev: $(INSTALL_DEV_STAMP)

$(INSTALL_DEV_STAMP): $(PYTHON) pyproject.toml
	$(UV) sync
	touch $(INSTALL_DEV_STAMP)

.PHONY: lint
lint: $(INSTALL_DEV_STAMP)
	$(UV) run ruff check
	$(UV) run ruff check --select I

.PHONY: format
format: $(INSTALL_DEV_STAMP)
	$(UV) run ruff check --select I --fix
	$(UV) run ruff format

.PHONY: database
database:
	docker-compose up -d database
	sleep 20
	cd ../database; yarn run db:update:local

.PHONY: data
data: \
	data/01_raw/xml/01_01.done \
	data/01_raw/MP_BASE_DATA/01_02.done \
	data/02_cached/electoral_term_pp20/stage_01/01_03.done

data/01_raw/xml/01_01.done: $(INSTALL_STAMP)
	$(PYTHON) src/$(NAME)/01_data/01_download_raw_data.py
	touch data/01_raw/xml/01_01.done

data/01_raw/MP_BASE_DATA/01_02.done: $(INSTALL_STAMP)
	$(PYTHON) src/$(NAME)/01_data/02_download_MdB_data.py
	touch data/01_raw/MP_BASE_DATA/01_02.done

data/02_cached/electoral_term_pp20/stage_01/01_03.done: $(INSTALL_STAMP)
	$(PYTHON) src/$(NAME)/01_data/03_download_raw_data_electoral_term_20.py
	touch data/02_cached/electoral_term_pp20/stage_01/01_03.done

.PHONY: process
process: \
	data/01_raw/txt/02_01.done \
	data/01_raw/txt/02_02.done \
	data/02_cached/electoral_term_pp20/stage_02/02_03.done \
	data/02_cached/politicians/stage_01/02_04.done \
	data/03_final/02_05.done


data/01_raw/txt/02_01.done: data/01_raw/xml/01_01.done
	$(PYTHON) src/$(NAME)/02_preprocessing/01_split_xml.py
	touch data/01_raw/txt/02_01.done

data/01_raw/txt/02_02.done: data/01_raw/xml/01_01.done
	$(PYTHON) src/$(NAME)/02_preprocessing/02_split_xml_electoral_term_1_and_2.py
	touch data/01_raw/txt/02_02.done

data/02_cached/electoral_term_pp20/stage_02/02_03.done: data/02_cached/electoral_term_pp20/stage_01/01_03.done
	$(PYTHON) src/$(NAME)/02_preprocessing/03_split_xml_electoral_term_20.py
	touch data/02_cached/electoral_term_pp20/stage_02/02_03.done

data/02_cached/politicians/stage_01/02_04.done: data/01_raw/MP_BASE_DATA/01_02.done
	$(PYTHON) src/$(NAME)/02_preprocessing/04_extract_mps_from_mp_base_data.py
	touch data/02_cached/politicians/stage_01/02_04.done

data/03_final/02_05.done: $(INSTALL_STAMP)
	$(PYTHON) src/$(NAME)/02_preprocessing/05_create_electoral_terms.py
	touch data/03_final/02_05.done

.PHONY: factions
factions: \
	data/02_cached/factions/stage_01/03_01.done \
	data/03_final/03_02.done

data/02_cached/factions/stage_01/03_01.done: data/02_cached/politicians/stage_01/02_04.done
	$(PYTHON) src/$(NAME)/03_factions/01_create_factions.py
	touch data/02_cached/factions/stage_01/03_01.done

data/03_final/03_02.done: data/02_cached/factions/stage_01/03_01.done
	$(PYTHON) src/$(NAME)/03_factions/02_add_abbreviations_and_ids.py
	touch data/03_final/03_02.done

.PHONY: politicians
politicians: \
	data/02_cached/politicians/stage_02/04_01.done \
	data/02_cached/politicians/stage_01/04_02.done \
	data/03_final/04_03.done

data/02_cached/politicians/stage_02/04_01.done: data/02_cached/politicians/stage_01/02_04.done data/03_final/03_02.done
	$(PYTHON) src/$(NAME)/04_politicians/01_add_faction_id_to_mps.py
	touch data/02_cached/politicians/stage_02/04_01.done

data/02_cached/politicians/stage_01/04_02.done: $(INSTALL_STAMP)
	$(PYTHON) src/$(NAME)/04_politicians/02_scrape_mgs.py
	touch data/02_cached/politicians/stage_01/04_02.done

data/03_final/04_03.done: data/02_cached/politicians/stage_02/04_01.done data/02_cached/politicians/stage_01/04_02.done data/03_final/03_02.done
	$(PYTHON) src/$(NAME)/04_politicians/03_merge_politicians.py
	touch data/03_final/04_03.done

.PHONY: speeches
speeches: \
	data/02_cached/speech_content/stage_01/05_01.done \
	data/02_cached/speech_content/stage_02/05_02.done \
	data/02_cached/speech_content/stage_03/05_03.done

data/02_cached/speech_content/stage_01/05_01.done: data/01_raw/txt/02_01.done
	$(PYTHON) src/$(NAME)/05_speech_content/01_extract_speeches.py
	touch data/02_cached/speech_content/stage_01/05_01.done

data/02_cached/speech_content/stage_02/05_02.done: data/02_cached/speech_content/stage_01/05_01.done data/03_final/03_02.done
	$(PYTHON) src/$(NAME)/05_speech_content/02_clean_speeches.py
	touch data/02_cached/speech_content/stage_02/05_02.done

data/02_cached/speech_content/stage_03/05_03.done: data/02_cached/speech_content/stage_02/05_02.done data/03_final/04_03.done
	$(PYTHON) src/$(NAME)/05_speech_content/03_match_names_speeches.py
	touch data/02_cached/speech_content/stage_03/05_03.done

.PHONY: process_term_20
process_term_20: \
	data/02_cached/electoral_term_pp20/stage_03/06_01.done \
	data/03_final/06_01.done \
	data/02_cached/contributions_extended/stage_01/06_01.done

data/02_cached/electoral_term_pp20/stage_03/06_01.done data/03_final/06_01.done data/02_cached/contributions_extended/stage_01/06_01.done: data/02_cached/electoral_term_pp20/stage_02/02_03.done data/03_final/03_02.done
	$(PYTHON) src/$(NAME)/06_electoral_term_20/01_extract_speeches_and_contributions_electoral_term_20.py
	touch data/02_cached/electoral_term_pp20/stage_03/06_01.done
	touch data/03_final/06_01.done
	touch data/02_cached/contributions_extended/stage_01/06_01.done

.PHONY: contributions
contributions: \
	data/02_cached/speech_content/stage_04/07_01.done \
	data/02_cached/contributions_extended/stage_01/07_01.done \
	data/03_final/07_01.done \
	data/02_cached/contributions_extended/stage_02/07_02.done \
	data/02_cached/contributions_extended/stage_03/07_03.done

data/02_cached/speech_content/stage_04/07_01.done data/02_cached/contributions_extended/stage_01/07_01.done data/03_final/07_01.done: data/02_cached/speech_content/stage_03/05_03.done data/03_final/03_02.done
	$(PYTHON) src/$(NAME)/07_contributions/01_extract_contributions.py
	touch data/02_cached/speech_content/stage_04/07_01.done
	touch data/02_cached/contributions_extended/stage_01/07_01.done
	touch data/03_final/07_01.done

data/02_cached/contributions_extended/stage_02/07_02.done: data/02_cached/contributions_extended/stage_01/07_01.done data/03_final/03_02.done
	$(PYTHON) src/$(NAME)/07_contributions/02_clean_contributions_extended.py
	touch data/02_cached/contributions_extended/stage_02/07_02.done

data/02_cached/contributions_extended/stage_03/07_03.done: data/02_cached/contributions_extended/stage_02/07_02.done data/03_final/04_03.done
	$(PYTHON) src/$(NAME)/07_contributions/03_match_contributions_extended.py
	touch data/02_cached/contributions_extended/stage_03/07_03.done

.PHONY: upload
upload: data/03_final/08_01.done \
data/03_final/08_02.done


data/03_final/08_01.done: data/01_raw/xml/01_01.done data/02_cached/speech_content/stage_04/07_01.done data/02_cached/electoral_term_pp20/stage_03/06_01.done data/02_cached/contributions_extended/stage_03/07_03.done
	$(PYTHON) src/$(NAME)/08_database/01_concat_everything.py
	touch data/03_final/08_01.done

data/03_final/08_02.done: data/03_final/08_01.done
	$(PYTHON) src/$(NAME)/08_database/02_upload_data_to_database.py
	touch data/03_final/08_02.done

.PHONY: full-run
full-run: data process factions politicians speeches process_term_20 contributions upload

.PHONY: clean
clean:
	rm -rf $(VENV_NAME)
	rm -rf .ruff_cache
	rm -rf open_discourse.egg-info
	rm -rf dist
	find . -name __pycache__ -type d -exec rm -r {} +

.PHONY: clean-data
clean-data:
	rm -rf data
