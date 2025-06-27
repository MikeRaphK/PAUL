# Install python and git
FROM python:3.12-slim
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Setup necessary files
COPY src/paul /app/src/paul
COPY main.py /app/main.py
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

# Get ready to execute PAUL
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["sh", "-c", "cd /app && python3 main.py \"$@\"", "--"]