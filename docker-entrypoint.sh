#!/bin/bash

# Wait for database
if [[ "$WAIT_FOR_DATABASE" = "1" ]]; then
    ./wait-for-it.sh "${DATABASE_HOST}:${DATABASE_PORT-5432} -t 15"
fi

# Setup local development environment
if [[ "$APPLY_MIGRATIONS" = "1" ]]; then
    python manage.py migrate --noinput
fi

if [[ "$GEO_IMPORT" = "1" ]]; then
    python manage.py geo_import --municipalities finland
    python manage.py geo_import --divisions helsinki
fi

if [[ "$RESOURCE_IMPORT" = "1" ]]; then
    python manage.py resources_import --all tprek
    python manage.py resources_import --all kirjastot
fi

if [[ "$COLLECT_STATIC" = "1" ]]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

# Create superuser
if [[ "$CREATE_SUPERUSER" = "1" ]]; then
    DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser -u admin -e admin@example.com
    echo "Admin user created with credentials admin:admin (email: admin@example.com)"
fi

if [[ ! -z "$@" ]]; then
    # When a command is passed, run that
    "$@"
elif [[ "$DEV_SERVER" = "1" ]]; then
    # If no command, and the dev server env var is true, run the dev server
    exec ./manage.py runserver 0.0.0.0:8000
else
    exec uwsgi --ini uwsgi.ini
fi
