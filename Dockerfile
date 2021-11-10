# ======================================================================
FROM python:3.8-buster AS app-base
# ======================================================================
WORKDIR /app

COPY --chown=appuser:appuser requirements.txt /app
RUN set -eux; \
    groupadd --gid 1000 appuser; \
    useradd --uid 1000 --gid appuser --create-home --shell /bin/bash appuser; \
    apt-get update; \
    apt-get install -y \
        gdal-bin \
        postgresql-client \
    ; \
    curl -sL https://deb.nodesource.com/setup_12.x | bash -; \
    apt-get install -y nodejs; \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
    rm -rf /var/lib/apt/lists/*; \
    rm -rf /var/cache/apt/archives; \
    pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# ======================================================================
FROM app-base AS development
# ======================================================================
COPY --chown=appuser:appuser dev-requirements.txt /app
RUN pip install --no-cache-dir -r dev-requirements.txt
COPY --chown=appuser:appuser . /app/
RUN ./build-resources
USER appuser
EXPOSE 8000/tcp

# ====================================================
FROM app-base AS production
# ====================================================
COPY --chown=appuser:appuser . /app/
RUN python manage.py collectstatic
USER appuser
EXPOSE 8000/tcp
