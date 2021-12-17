#!/bin/bash

# Wait for database
if [[ "$WAIT_FOR_DATABASE" = "1" ]]; then
    wait-for-it.sh "${DATABASE_HOST}:${DATABASE_PORT-5432}"
fi

if [[ "$APPLY_MIGRATIONS" = "1" ]]; then
    python manage.py migrate --noinput
fi

if [[ ! -z "$@" ]]; then
    # When a command is passed, run that
    "$@"
elif [[ "$DEV_SERVER" = "1" ]]; then
    exec ./manage.py runserver 0.0.0.0:8000
else
    uwsgi --ini .prod/uwsgi.ini
fi
