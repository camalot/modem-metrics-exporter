# Dockerfile for netprobe_lite
# https://github.com/plaintextpackets/netprobe_lite/

# Default to amd64 if no build argument is provided
ARG BASE_IMAGE_ARCH=amd64
# Default to Python 3.12 if no build argument is provided
ARG PYTHON_VERSION=3.12

# slim-bookworm
FROM ${BASE_IMAGE_ARCH}/python:${PYTHON_VERSION}-alpine

ARG BRANCH="develop"
ARG BUILD_VERSION="1.0.0-snapshot"
ARG PROJECT_NAME=netprobe_lite

ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV NP_MODULE=FULL

LABEL VERSION="${BUILD_VERSION}"
LABEL BRANCH="${BRANCH}"
LABEL PROJECT_NAME="${PROJECT_NAME}"

USER root:root

WORKDIR /app

# Copy application code
COPY ./src/ /app/
# copy default configuration file
COPY ./modemprobe.yaml /config/modemprobe.yaml

RUN \
    apk update \
    && apk add --no-cache bash git curl build-base tcl tk iputils-ping \
    && mkdir -p /data /config /app/logs \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/setup/requirements.txt \
    && apk del git build-base \
    && rm -rf /app/setup \
    && ln -s /app/logs /logs \
    && chown -R 1000:1000 /app /data /logs /config

EXPOSE 5000

VOLUME [ "/data" ]
VOLUME [ "/config" ]

USER 1000:1000

ENTRYPOINT [ "python3", "/app/main.py" ]
