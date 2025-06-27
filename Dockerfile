# Install python and git
FROM python:3.12-slim
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Setup working directory and necesarry files
WORKDIR /app
COPY requirements.txt /app/requirements.txt
COPY src/paul /app/src/paul
COPY main.py /app/main.py
RUN pip3 install -r requirements.txt

# Get ready to execute PAUL
ENV PYTHONUNBUFFERED=1
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]