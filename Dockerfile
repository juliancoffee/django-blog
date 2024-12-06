# Ok, so this Docker image combines two processes into one
#
# One to run Django and handle requests
# One to run nginx and server static files
#
# I know that Docker hates this kind of stuff, and I sort of hate it too
# because logs are intermingled now and all that stuff
#
# But as I don't want to spin entire infrastructure to host static files
# this will do
#
# Maybe at some point I will spin entire CI/CD thing, but not today
#
# so yeah, sorry about that
FROM nginx:1.27

# get ready to launch nginx
COPY nginx.conf /etc/nginx/nginx.conf

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
ARG STATIC_ROOT
ARG DJANGO_SUPERUSER_PASSWORD

# well, if you want to set environmental variables, you need to set them
# no magic for you here
#
# so I did
# p. s. Docker doesn't like that I'm doing this, but idk
ENV SECRET_KEY=${SECRET_KEY}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_HOST=${DB_HOST}
ENV STATIC_ROOT=${STATIC_ROOT}
ENV DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD}

# Python stuff
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# p. s. this one copies entire folder
# and I'm not sure if it follows .dockerignore file
ADD . /app
WORKDIR /app
# init the environment, uv docs told me to do that
# p. p. s. it seems that I don't need to download Python in dockerfile
# but maybe I'd rather did it to speed things up
RUN uv sync --frozen

# run both Django and nginx with a single script
ENTRYPOINT ["/bin/sh", "serve_script.sh"]
