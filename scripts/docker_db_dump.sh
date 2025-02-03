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
    printf "\x1b[33m" # green for success
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

print_green "loading the script to the container..."
docker cp scripts/backup_dump.sh "$container":backup.sh

print_green "script to execute..."
docker exec "$container" cat backup.sh

print_green "executing..."
docker exec "$container" bash backup.sh

print_green "copying the result..."
if [ -z "${2:-}" ]
then
    res="dump$(date -Iseconds).sql"
else
    res="$2"
fi

if [ -f "$res" ]
then
    echo "you sure you want to overwrite the file? y/N"
    read answer
    case "$answer" in
        "y")
            ;;
        *)
            echo "i thought so"
            exit
            ;;
    esac
fi
docker cp "$container":dump.sql - | tar -x --to-stdout > "$res"

print_green "protecting from writes..."
chmod -w $res

print_green "done."
ls -lth $res
