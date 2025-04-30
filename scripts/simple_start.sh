#!/usr/bin/env bash

docker compose -f docker-compose-db.yml up &

# wait for db to start
for i in 3 2 1; do
  echo "<> waiting $i second(s) for DB to start"
  sleep 1
done

# run migrations
echo "<> run migrations"
uv run manage.py migrate

# start the debugger
echo "<> ready to launch"
uv run python manage.py runserver 0.0.0.0:8000
