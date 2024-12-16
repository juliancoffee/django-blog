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

# set up the app
WORKDIR /app

# install dependencies first, for better caching behaviour
# recommended by uv and Docker best practices
#
# note that we're using bind here, so no files will be persisted into image
# layers, at least at this stage
#
# the practical effect of this is that if dependencies don't change the layer
# gets cached, which speeds up the building process A LOT, since this is the
# task that consumes the most of it
#
# --frozen means "don't update lockfile" btw
RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# now install the rest of the project (without dev dependencies)
COPY . /app
RUN uv sync --frozen --no-dev

ENTRYPOINT ["/bin/sh", "serve_script.sh"]
