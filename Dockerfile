FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && addgroup --system app \
    && adduser --system --ingroup app app \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml manage.py README.md /app/
COPY config /app/config
COPY apps /app/apps
COPY requirements /app/requirements
COPY scripts/entrypoint.sh /app/scripts/

RUN pip install --upgrade pip \
    && pip install -r /app/requirements/base.txt \
    && chmod +x /app/scripts/entrypoint.sh \
    && chown -R app:app /app

USER app

ENTRYPOINT ["/app/scripts/entrypoint.sh"]

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
