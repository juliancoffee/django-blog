FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# So I don't actually know if I need to do any of that, really
# but it doesn't seem to work otherwise, idk
#
# First, I list build args to provide some way to get environmental
# variables
#
# I'm not sure if I need to do that, but when I tried using plain `docker
# build`, it refused to grab them at all
#
# maybe now that I back with docker-compose, this will work now?
#
# and I've read that render.io docker worker grabs this stuff from env vars
# as well
#
# so let them be
ARG SECRET_KEY
ARG DB_PASSWORD
ARG DB_HOST
ARG DJANGO_SUPERUSER_PASSWORD

# well, if you want to set environmental variables, you need to set them
# no magic for you here
#
# so I did
# p. s. Docker doesn't like that I'm doing this, but idk
ENV SECRET_KEY=${SECRET_KEY}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_HOST=${DB_HOST}
ENV DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD}

# set the app
WORKDIR /app
COPY . /app

# install everything
#
# probably could be improved by splitting dependency installs and project
# installation
RUN uv sync --frozen

ENTRYPOINT ["/bin/sh", "serve_script.sh"]
