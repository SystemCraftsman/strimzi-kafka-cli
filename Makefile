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
	python -m pytest -x

build: clean
	python setup.py sdist bdist_wheel
