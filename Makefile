SHELL := /bin/bash

PYPI_USER=
PYPI_SERVER=

DIST_FILES=dist/$(shell ls -1A dist)
PIP_LOG=pip-log.txt

default: build

clean:
	-rm -rf dist build .eggs *.egg-info ${PIP_LOG}

lint:
	python -m flake8

test:
	python -m pytest

build: clean
	python -m build; twine check --strict dist/*

install-dependencies:
	pip install ".[dev]"
