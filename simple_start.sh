#!/usr/bin/env sh

control_c() {
    docker compose down
    exit
}

trap control_c SIGINT

cd dev/
docker compose up
