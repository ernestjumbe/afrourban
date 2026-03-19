# syntax=docker/dockerfile:1.4

# pull official base image
FROM --platform=$BUILDPLATFORM python:3.11.4-slim-buster AS builder

EXPOSE 8000
# set work directory
WORKDIR /app

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    LIBRARY_PATH=/lib:/usr/lib \
    # Poetry's configuration:
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local' \
    POETRY_VERSION=1.8.3 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    # dependencies for building Python packages
    && apt-get install -y build-essential \
    # psycopg2 dependencies
    && apt-get install -y libpq-dev \
    # Translations dependencies
    && apt-get install -y gettext \
    # Additional dependencies
    && apt-get install -y git \
    # Geo dependencies
    && apt-get install -y gdal-bin libgdal-dev\
    && apt-get install -y python3-gdal \
    && apt-get install -y binutils libproj-dev gdal-bin \
    && apt-get install -y make \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && poetry --version \
    # cleaning up unused files
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 -


COPY . /app
RUN make install


COPY ./compose/staging/django/start /start
RUN sed -i 's/\r$//g' /start \
    && chmod +x /start



FROM builder as dev-envs
RUN <<EOF
apt-get update -y
apt-get install git -y
EOF

WORKDIR /app

ENTRYPOINT ["/entrypoint"]