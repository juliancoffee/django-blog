#!/usr/bin/env bash
set -o errexit

echo "<> installing dependencies"
pip install -r requirements_lock.txt

echo "<> collecting static files"
python manage.py collectstatic --no-input

echo "<> running migrations"
python manage.py migrate

echo "<> creating superuser"
# technically, this could be hidden, but uh
create_super() {
python manage.py createsuperuser \
    --username admin \
    --email admin@example.com \
    --noinput
}
# supress failures if superuser exists
create_super || true
