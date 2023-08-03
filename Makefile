PYPI_USER=
PYPI_SERVER=

DIST_FILES=dist/$(shell ls -1A dist)
PIP_LOG=pip-log.txt

default: build

clean:
	-rm -rf dist build .eggs *.egg-info ${PIP_LOG}

lint:
	python -m flake8 --extend-ignore=E203,E231,E501 --count

format:
	python -m black .; python -m docformatter -r kfk; python -m docformatter -r tests

test:
	pushd tests; python -m pytest -x; popd

build: clean
	python setup.py sdist bdist_wheel
