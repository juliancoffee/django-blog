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
export DEBUG_LOG_VIEW=1

#export CONSOLE_LOG_LEVEL=INFO # default is DEBUG
export PYLOG_LEVEL=DEBUG # default is INFO
#export GUNICORN_LOG_LEVEL=DEBUG # default is INFO
#export DJANGO_LOG_LEVEL=DEBUG # default is INFO

# clear debug log at startup
# is it a wise move? idk
# but I can't think of a better solution for now
echo "" > debug.log

# NOTE: use `exec` here to seize control, helps if you wanna Ctrl+C
#
# runserver has hot-reload, so that's what we use
#exec python manage.py runserver 0.0.0.0:8000
exec gunicorn mysite.wsgi --bind 0.0.0.0:8000 --access-logfile -
