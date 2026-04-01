FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install selenium pyperclip pyjson5

WORKDIR /app

COPY message_engine.py .
COPY integration_daemon.py .
COPY train_model.py .

CMD ["python3", "integration_daemon.py"]
