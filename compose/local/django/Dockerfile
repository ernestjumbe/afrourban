# syntax=docker/dockerfile:1.4

# ============================================
# Stage 1: Builder - Install dependencies and build
# ============================================
FROM python:3.12-slim AS builder

# Set work directory
WORKDIR /app

# Environment variables for Python and Poetry
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
    POETRY_VERSION=2.2.1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Dependencies for building Python packages
    build-essential \
    # psycopg2 build dependencies
    libpq-dev \
    # Translations dependencies
    gettext \
    # Git for poetry dependencies
    git \
    # Geo dependencies
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    binutils \
    libproj-dev \
    # Make for project build
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && poetry --version

# Copy dependency files first (for better layer caching)
COPY pyproject.toml poetry.lock* Makefile ./

# Install Python dependencies (dev) via Make
RUN make install-dev

# Copy the rest of the application
COPY . .

# ============================================
# Stage 2: Runtime - Development image with debugging tools
# ============================================
FROM python:3.12-slim AS runtime

# Expose application port
EXPOSE 8000

# Set work directory
WORKDIR /app

# Environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    DJANGO_SETTINGS_MODULE=afrourban.settings.local \
    # Application user
    APP_USER=afrourban \
    APP_GROUP=afrourban \
    APP_UID=1000 \
    APP_GID=1000

# Install runtime dependencies (includes dev tools for local development)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # psycopg2 runtime dependency (crucial for PostgreSQL connection)
    libpq5 \
    # Translations runtime
    gettext \
    # Geo runtime dependencies
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    binutils \
    # Development tools for local environment
    git \
    vim \
    curl \
    wget \
    # Make for entrypoint scripts
    make \
    && rm -rf /var/lib/apt/lists/*

# Create afrourban user and group
RUN groupadd -g ${APP_GID} ${APP_GROUP} \
    && useradd -u ${APP_UID} -g ${APP_GROUP} -m -s /bin/bash ${APP_USER}

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=${APP_USER}:${APP_GROUP} . /app

# Copy and prepare entrypoint scripts
COPY --chown=${APP_USER}:${APP_GROUP} ./compose/local/django/entrypoint /entrypoint
COPY --chown=${APP_USER}:${APP_GROUP} ./compose/local/django/start /start
COPY --chown=${APP_USER}:${APP_GROUP} ./compose/local/celery/flower/start /start-flower
COPY --chown=${APP_USER}:${APP_GROUP} ./compose/local/celery/beat/start /start-celerybeat

# Fix line endings and set permissions
RUN sed -i 's/\r$//g' /entrypoint \
    && sed -i 's/\r$//g' /start \
    && sed -i 's/\r$//g' /start-flower \
    && sed -i 's/\r$//g' /start-celerybeat \
    && chmod +x /entrypoint /start /start-flower /start-celerybeat

# Create necessary directories with proper ownership
RUN mkdir -p /app/staticfiles /app/mediafiles \
    && chown -R ${APP_USER}:${APP_GROUP} /app

# Switch to non-root user
USER ${APP_USER}

ENTRYPOINT ["/entrypoint"]
