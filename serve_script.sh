# Dockerfile entry point

echo "<> running migrations"
time python manage.py migrate

echo "<> collecting statics"
time python manage.py collectstatic --no-input

echo "<> creating superuser"
# noinput here also means that password is taken from env variable
# DJANGO_SUPERUSER_PASSWORD
time python manage.py createsuperuser \
    --username admin \
    --email admin@example.com \
    --noinput

echo "<> running the server"
#export DJDT=1
#export DEBUG=1
export PYLOG_LEVEL=DEBUG
export DJANGO_LOG_LEVEL=DEBUG
export DEBUG_LOG_VIEW=1

# clear debug log at startup
# is it a wise move? idk
# but I can't think of a better solution for now
echo "" > debug.log

# NOTE: use `exec` here to seize control, helps if you wanna Ctrl+C
#
# runserver has hot-reload, so that's what we use
exec python manage.py runserver 0.0.0.0:8000
#exec uv run gunicorn mysite.wsgi --bind 0.0.0.0:8000
