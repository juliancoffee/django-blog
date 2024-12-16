# Dockerfile entry point

echo "<> running migrations"
uv run manage.py migrate

# run Django in the background
echo "<> collecting statics"
# noinput here should also ignore any warnings
# like if staticfile folder is already present and it asks to overwrite
uv run manage.py collectstatic --no-input

echo "<> creating superuser"
# noinput here also means that password is taken from env variable
# DJANGO_SUPERUSER_PASSWORD
uv run manage.py createsuperuser \
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
