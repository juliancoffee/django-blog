#!/usr/bin/env sh

# based on ./howto_backup.sh

# re-create db
dropdb -U postgres postgres
createdb -U postgres postgres

# re-populate from backup
psql -U postgres --single-transaction < dump.sql
