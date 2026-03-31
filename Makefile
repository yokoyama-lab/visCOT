.PHONY: all test clean install lint svg

all: test

install:
	pip install -e ".[dev]" --break-system-packages

test:
	python3 -m pytest tests/ -q

svg:
	python3 -m pytest tests/test_canvas.py::TestExhaustive \
		tests/test_canvas.py::TestNoSplineCrossings \
		tests/test_canvas.py::TestSmallCrossings \
		tests/test_canvas.py::TestStress \
		-v --save-images=test_output/svg --image-format=svg

lint:
	python3 -m ruff check src/ tests/
	python3 -m mypy src/

clean:
	$(RM) -rf src/viscot/__pycache__ src/viscot/core/__pycache__
	$(RM) -rf tests/__pycache__ .pytest_cache
	$(RM) -f .coverage
	$(RM) -f src/viscot/core/parser.out src/viscot/core/parsetab.py
	$(RM) -rf test_output/
