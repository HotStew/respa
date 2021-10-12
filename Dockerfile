# ======================================================================
FROM python:3.6-alpine AS app-base
# ======================================================================
WORKDIR /app
COPY --chown=appuser:appuser requirements.txt /app

RUN addgroup -S appuser && adduser -S appuser -G appuser && \
      apk add --no-cache --virtual .build-deps \
      build-base \
      python3-dev \
      libffi-dev \
    && apk add --no-cache \
      bash \
      coreutils \
      jpeg-dev \
      zlib-dev \
      libxml2-dev \
      libxslt-dev \
      gdal-dev \
      postgresql-dev \
      pcre-dev \
      pcre \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && rm -r /root/.cache \
    && apk del .build-deps

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
