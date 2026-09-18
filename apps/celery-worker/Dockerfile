# M0-01: full Compose wiring belongs to #3.
FROM python:3.12-slim AS base
WORKDIR /srv/celery-worker
COPY apps/celery-worker/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/celery-worker ./
CMD ["celery", "-A", "app.celery_app.celery", "worker", "--loglevel=info", "--queues=nerveops-shell"]
