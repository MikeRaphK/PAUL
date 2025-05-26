FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY src/paul ./src/paul
COPY main.py .

ENTRYPOINT ["python", "main.py"]