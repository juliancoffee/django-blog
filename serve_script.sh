# Dockerfile entry point

echo "<> running migrations"
uv run manage.py migrate

# run Django in the background
echo "<> static root is: $STATIC_ROOT"
# I have zero idea why this command is needed
# I'd expect docker to spin a fresh new image without old data, but idk
# so I do this just in case
if [ -d "$STATIC_ROOT" ]
then
    echo "<> $STATIC_ROOT is dirty, cleaning it"
    rm -rf "$STATIC_ROOT"
fi
uv run manage.py collectstatic

echo "<> creating superuser"
uv run manage.py createsuperuser \
    --username admin \
    --email admin@example.com \
    --noinput

echo "<> running the server"
#export DEBUG=1
#uv run manage.py runserver 0.0.0.0:8000
uv run gunicorn -w 4 mysite.wsgi --bind 0.0.0.0:8000
