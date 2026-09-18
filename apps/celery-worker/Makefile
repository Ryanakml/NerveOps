.PHONY: build start lint type-check test integration-test

build:
	pip install -r requirements.txt
	python3 -m compileall app

start:
	celery -A app.celery_app.celery worker --loglevel=$${LOG_LEVEL:-info} --queues=nerveops-shell

lint:
	python3 -m py_compile $$(find app -name '*.py')

type-check:
	python3 ../../scripts/check-python-shells.py --only celery-worker

test:
	python3 -m pytest tests -q

integration-test:
	python3 -m app.check --check
