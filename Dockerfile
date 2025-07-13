FROM python:3.12-slim

# System dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Poetry
RUN pip install poetry==2.1.3
ENV POETRY_VIRTUALENVS_CREATE=false

# Output Python logs instantly
ENV PYTHONUNBUFFERED=1

# Setup PAUL
COPY . /app/
RUN poetry install --directory /app --no-interaction --no-ansi

# Always start in the /app directory
WORKDIR /app