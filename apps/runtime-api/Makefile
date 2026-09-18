.PHONY: build start lint type-check test integration-test

build:
	pip install -r requirements.txt
	python3 -m compileall app

start:
	uvicorn app.main:app --host 0.0.0.0 --port $${RUNTIME_API_PORT:-8000}

lint:
	python3 -m py_compile $$(find app -name '*.py')

type-check:
	python3 ../../scripts/check-python-shells.py --only runtime-api

test:
	python3 -m pytest tests -q

integration-test:
	bash ../../scripts/check-shell-http.sh runtime-api http://localhost:8000/health
