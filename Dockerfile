# =============================================================================
# Production Dockerfile for SWAPI Voting API
# =============================================================================
# Author: Thomas Bournaveas
# -----------------------------------------------------------------------------

FROM python:3.12.10-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 8000

LABEL org.opencontainers.image.title="SWAPI Voting API" \
      org.opencontainers.image.description="Production image for FastAPI-powered SWAPI Voting microservice." \
      org.opencontainers.image.version="1.0.0" \
      maintainer="Thomas Bournaveas <thomas.bournaveas@gmail.com>"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
