FROM ghcr.io/astral-sh/uv:python3.12-alpine

WORKDIR /usr/src/app

COPY pyproject.toml .
COPY uv.lock . 

COPY *.py .

RUN uv sync --locked
