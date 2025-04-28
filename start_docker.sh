#!/usr/bin/env sh

# They promise better performance, and who am I to argue
export COMPOSE_BAKE=true

# I can't think of another way to force it to make it read Dockerfile and
# `docker-compose` it again, so here
docker compose build web

# start all other containers
docker compose up --watch --remove-orphans
