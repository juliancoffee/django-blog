# Dockerfile entry point

echo "<> collect static files"
# Ok
#
# we could put this into Dockerfile, yes
#
# but it will run basically each time anyway, because it's impossible to cache
# as it requires basically whole project and everything after `COPY . .` will
# be invalidated
#
# add to this that django does its management work on first command invocation
# and it takes about 7 seconds of "something"
#
# it sucks, but then again, maybe 7 seconds isn't that big of a deal?
time uv run manage.py collectstatic --no-input

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
#uv run manage.py runserver 0.0.0.0:8000

# NOTE: use `exec` here to make gunicorn the main process
# helps with interrupts
exec uv run gunicorn \
    -w 4 \
    --bind 0.0.0.0:8000 \
    mysite.wsgi
