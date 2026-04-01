FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    chromium-browser \
    chromium-driver \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    selenium \
    scikit-learn \
    numpy

WORKDIR /app

COPY main.py .
COPY whatsapp_integration.py .
COPY advanced_engine.py .
COPY message_parser.py .

ENV DISPLAY=:99

CMD ["python3", "main.py"]
