# M0-01: full Compose wiring belongs to #3.
FROM python:3.12-slim AS base
WORKDIR /srv/runtime-api
COPY apps/runtime-api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/runtime-api ./
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
