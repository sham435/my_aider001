FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD uvicorn src.web.app:app --host 0.0.0.0 --port ${PORT:-8000}