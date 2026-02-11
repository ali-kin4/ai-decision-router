PYTHON ?= python

setup:
	$(PYTHON) -m pip install -e .[dev]

test:
	pytest

lint:
	ruff check src tests

fmt:
	black src tests
	ruff check src tests --fix

bench:
	router bench --suite quick
