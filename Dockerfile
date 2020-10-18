FROM python:3.9-alpine

WORKDIR /srv

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.1.3

RUN apk --no-cache -U upgrade \
    && apk add --no-cache \
        gcc \
        musl-dev \
        python3-dev \
        libffi-dev \
        openssl-dev \
        build-base

RUN pip install "poetry==$POETRY_VERSION"
COPY pyproject.toml poetry.lock ./

RUN poetry install --no-dev --no-interaction --no-ansi

COPY ./app /srv/app
