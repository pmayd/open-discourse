# see https://blog.mathieu-leplatre.info/tips-for-your-makefile-with-python.html
NAME := open_discourse
VENV := $(shell echo $${VIRTUAL_ENV-.venv})
PY3 := $(shell command -v python3 2> /dev/null)
PYTHON := $(VENV)/bin/python
INSTALL_STAMP := $(VENV)/.install.stamp
INSTALL_DEV_STAMP := $(VENV)/.install.dev.stamp

.DEFAULT_GOAL = install-dev

$(PYTHON):
	@if [ -z $(PY3) ]; then echo "Python 3 could not be found."; exit 2; fi
	$(PY3) -m venv $(VENV)

.PHONY: install
install: $(INSTALL_STAMP)

$(INSTALL_STAMP): $(PYTHON) pyproject.toml
	$(PYTHON) -m pip install -U pip
	$(PYTHON) -m pip install -e .
	touch $(INSTALL_STAMP)

.PHONY: install-dev
install-dev: $(INSTALL_DEV_STAMP)

$(INSTALL_DEV_STAMP): $(PYTHON) pyproject.toml
	$(PYTHON) -m pip install -U pip
	$(PYTHON) -m pip install -e .[dev]
	touch $(INSTALL_DEV_STAMP)

.PHONY: lint
lint: $(INSTALL_DEV_STAMP)
	${VENV_PYTHON} -m ruff check
	${VENV_PYTHON} -m ruff check --select I

.PHONY: format
format: $(INSTALL_DEV_STAMP)
	${VENV_PYTHON} -m ruff check --select I --fix
	${VENV_PYTHON} -m ruff format

.PHONY: database
database:
	docker-compose up -d database
	sleep 20
	cd ../database; yarn run db:update:local

.PHONY: data
data: \
	data/01_raw/xml \
	data/01_raw/MP_BASE_DATA \
	data/02_cached/electoral_term_19_20/stage_01

data/01_raw/xml: $(INSTALL_STAMP)
	$(PYTHON) src/$(NAME)/01_data/01_download_raw_data.py

data/01_raw/MP_BASE_DATA: $(INSTALL_STAMP)
	$(PYTHON) src/$(NAME)/01_data/02_download_MdB_data.py

data/02_cached/electoral_term_19_20/stage_01: $(INSTALL_STAMP)
	$(PYTHON) src/$(NAME)/01_data/03_download_raw_data_electoral_term_19_20.py

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
