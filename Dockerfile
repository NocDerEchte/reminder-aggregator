FROM python:3.13-slim

LABEL description="Code-Reminder aggregation tool"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd --system app && \
    useradd --system --create-home --gid app app

COPY reminder_aggregator.py .

RUN chown -R app:app /app && \
    chmod -R 755 /app

USER app:app

ENTRYPOINT [ "python3", "./reminder_aggregator.py" ]
