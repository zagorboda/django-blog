#!/bin/sh

python manage.py makemigrations --no-input

python manage.py migrate

CONTAINER_ALREADY_STARTED="../CONTAINER_ALREADY_STARTED"
if [ ! -e $CONTAINER_ALREADY_STARTED ]; then
    touch $CONTAINER_ALREADY_STARTED

    python scripts/populate_db.py
    python scripts/init_admin.py

fi

python manage.py runserver 0.0.0.0:8000