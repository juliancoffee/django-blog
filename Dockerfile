FROM ghcr.io/astral-sh/uv:python3.12-alpine

# Don't cache index to reduce size
# Btw, the reason why I install bash is that I can use time command in scripts
RUN apk add --no-cache bash dumb-init
#RUN apk add --no-cache neovim

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

# drop `uv` at that point, and use plain python tools
#
# if you don't, and continue to use `uv run`, keep in mind that `uv run`
# will try to load ALL the dependencies, including dev ones, as we didn't cache
# them above, so you'll get quite a cache miss
ENV PATH="/app/.venv/bin:$PATH"

# collect statics
#
# so, idk where to put them
#
# if I put them there, `sync+restart` in `compose watch` is faster
# if I put them in ./serve_script.sh, I don't need to use `rebuild` if I change
# static files
#
# fyi, it takes about 2 seconds on my machine at the time of writing
#RUN python manage.py collectstatic --no-input

ENTRYPOINT ["dumb-init", "--", "/bin/bash", "scripts/entrypoint_docker.sh"]
