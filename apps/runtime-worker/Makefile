.PHONY: build start lint type-check test integration-test

build:
	pip install -r requirements.txt
	python3 -m compileall worker

start:
	python3 -m worker.main

lint:
	python3 -m py_compile $$(find worker -name '*.py')

type-check:
	python3 ../../scripts/check-python-shells.py --only runtime-worker

test:
	python3 -m pytest tests -q

integration-test:
	python3 -m worker.main --check
	python3 -m worker.main --once
