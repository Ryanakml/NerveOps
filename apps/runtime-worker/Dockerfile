# M0-01: full Compose wiring belongs to #3.
FROM python:3.12-slim AS base
WORKDIR /srv/runtime-worker
COPY apps/runtime-worker/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/runtime-worker ./
CMD ["python", "-m", "worker.main"]
