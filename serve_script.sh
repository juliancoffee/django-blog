# Dockerfile entry point

echo "<> running migrations"
time uv run manage.py migrate

echo "<> creating superuser"
# noinput here also means that password is taken from env variable
# DJANGO_SUPERUSER_PASSWORD
time uv run manage.py createsuperuser \
    --username admin \
    --email admin@example.com \
    --noinput

echo "<> running the server"
#export DEBUG=1

# NOTE: use `exec` here to seize control, helps if you wanna Ctrl+C
#
# runserver has hot-reload, so ...
exec uv run manage.py runserver 0.0.0.0:8000
#exec uv run gunicorn mysite.wsgi --bind 0.0.0.0:8000
