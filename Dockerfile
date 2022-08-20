ARG PYIMAGE=python:3.9-alpine3.16

FROM ${PYIMAGE} AS builder
LABEL maintainer="William Chavula <rumbani@gmail.com>"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIPENV_VENV_IN_PROJECT=1

WORKDIR /tmp/api
RUN mkdir /tmp/api/.venv

RUN apk update && apk add libpq-dev gcc
COPY Pipfile.lock .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install pipenv \
    && pipenv requirements --dev > requirements.txt


FROM ${PYIMAGE}
LABEL maintainer="William Chavula <rumbani@gmail.com>"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apk update \
    && apk add build-base \
    && apk add libffi-dev \
    && apk add libpq-dev gcc libuv-dev \
    && rm -rf /var/cache/apk/*

WORKDIR /api
COPY --from=builder /tmp/api/requirements.txt /api/requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
