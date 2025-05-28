# syntax=docker/dockerfile:1.4

# ---- Build stage ----
FROM python:3.13.3-slim AS builder
WORKDIR /app

# System deps for building wheels, psycopg2, etc.
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
COPY requirements-dev.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---- Production image ----
FROM python:3.13.3-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# System deps for runtime
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app source
COPY . .

# Use non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Expose FastAPI default port
EXPOSE 8000

# Healthcheck endpoint
HEALTHCHECK CMD curl --fail http://localhost:8000/ || exit 1

# Start with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
