#!/usr/bin/env bash

set -euo pipefail

print_red() {
    printf "\x1b[31m" # red for error
    echo "$@"
    printf "\x1b[0m" # reset color
}

print_green() {
    printf "\x1b[32m" # green for success
    echo "$@"
    printf "\x1b[0m" # reset color
}

print_yellow() {
    printf "\x1b[33m" # yellow for warning
    echo "$@"
    printf "\x1b[0m" # reset color
}

if [ -z "${1:-}" ]
then
    print_red "provide container's name as a first argument, error"
    docker container list
    print_yellow "note: you need NAMES, that's the last column"
    exit 1
else
    container="$1"
fi

if [ -z "${2:-}" ]
then
    print_red "provide dump sql file as a second argument, error"
    exit 1
else
    dump_sql="$2"
fi

print_green "loading the script to the container..."
docker cp scripts/backup_restore.sh "$container":restore.sh

print_green "script to execute..."
docker exec "$container" cat restore.sh

print_green "loading the backup file..."
docker cp "$dump_sql" "$container":dump.sql
docker exec "$container" ls -lth dump.sql

print_green "executing..."
docker exec "$container" bash restore.sh

print_green "done."
