.PHONY: all test clean install lint

all: test

install:
	pip install -e ".[dev]" --break-system-packages

test:
	python3 -m pytest tests/ -q

lint:
	python3 -m ruff check src/ tests/
	python3 -m mypy src/

clean:
	$(RM) -rf src/viscot/__pycache__ src/viscot/core/__pycache__
	$(RM) -rf tests/__pycache__ .pytest_cache
	$(RM) -f .coverage
	$(RM) -f src/viscot/core/parser.out src/viscot/core/parsetab.py
