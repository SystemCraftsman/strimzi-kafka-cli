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
	python -m pytest --ignore=tests/integration

test-integration:
	python -m pytest tests/integration -v

test-all: test test-integration

cluster-up:
	bash tests/integration/cluster-setup.sh

cluster-down:
	bash tests/integration/cluster-teardown.sh

build: clean
	python -m build; twine check --strict dist/*

install-dependencies:
	pip install ".[dev]"
