#!/usr/bin/env sh

# I can't think of another way to force it to make it read Dockerfile and
# docker-compose again, so here
docker compose up -d --build web

# start all other containers
docker compose up --watch --remove-orphans
