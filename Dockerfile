FROM ghcr.io/astral-sh/uv:python3.13-alpine

LABEL description="Code-Reminder aggregation tool"

WORKDIR /work

RUN uv pip install --system reminder-aggregator

ENTRYPOINT ["reminder-aggregator"]
