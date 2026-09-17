SHELL := /bin/bash

-include .env

PYTHON_BIN ?= python3.14

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
IMAGE_ANALYZER := $(VENV)/bin/image-analyzer

.PHONY: all venv install bootstrap doctor clean

all: install

venv:
	@test -x "$$(command -v $(PYTHON_BIN))" || \
		(echo "Python executable not found: $(PYTHON_BIN)" && exit 1)
	@test -d $(VENV) || $(PYTHON_BIN) -m venv $(VENV)

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -e '.[local,openai]'

bootstrap: install
	$(IMAGE_ANALYZER) bootstrap

doctor: install
	$(IMAGE_ANALYZER) doctor

clean:
	rm -rf $(VENV) build dist *.egg-info src/*.egg-info