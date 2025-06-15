FROM python:3.11-slim

WORKDIR /app

COPY airforce_report.pdf /app/airforce_report.pdf

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY logging_config.py .
COPY document.py .
COPY page.py .

ENV PDF_PATH=/app/airforce_report.pdf

ENTRYPOINT ["python", "main.py"]
