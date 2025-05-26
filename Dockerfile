# Dockerfile for building image of AI backend - Phinx 
# Stage 1: Builder
FROM python:3.11.9-bookworm AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN python -m venv .venv
COPY requirements.txt ./
RUN .venv/bin/pip install -r requirements.txt

# Stage 2: Final image
FROM python:3.11.9-slim-bookworm

WORKDIR /app

COPY --from=builder /app/.venv .venv/
COPY . .

# RUN apt-get update && apt-get install -y ca-certificates


# CMD ["/app/.venv/bin/python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# CMD ["/app/.venv/bin/python", "main.py"]
CMD ["/app/.venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8501", "--loop", "asyncio"]

