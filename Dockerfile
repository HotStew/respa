# ======================================================================
FROM python:3.6 AS app-base
# ======================================================================
WORKDIR /app
COPY --chown=appuser:appuser requirements.txt /app

RUN groupadd -g 1000 appuser && useradd -g 1000 -l -M -s /bin/false -u 1000 appuser && \
      apt-get update && apt-get install -y \
      gdal-bin \
      postgresql-client && \
      apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
      rm -rf /var/lib/apt/lists/* && \
      rm -rf /var/cache/apt/archives \
    && pip install --no-cache-dir -r /app/requirements.txt

ENTRYPOINT ["./docker-entrypoint.sh"]

# ============================
FROM app-base AS development
# ============================
COPY --chown=appuser:appuser dev-requirements.txt /app

RUN pip install --no-cache-dir -r /app/dev-requirements.txt

USER appuser
COPY --chown=appuser:appuser . /app/

EXPOSE 8000/tcp

# ==========================================================
FROM app-base AS production
# ==========================================================
COPY --chown=appuser:appuser . /app/

RUN python manage.py collectstatic
EXPOSE 8000/tcp
