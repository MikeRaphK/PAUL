FROM python:3.12-slim

# System dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Output Python logs instantly
ENV PYTHONUNBUFFERED=1

# Setup PAUL
COPY src/ /app/src/
COPY main.py /app/main.py
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

# Always start in the /app directory
WORKDIR /app