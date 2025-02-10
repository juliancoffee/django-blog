#!/usr/bin/env sh
# based on ./howto_backup.sh
set -euo pipefail

rollback() {
    echo ":( couldn't restore from backup, rollback to copy"
    if ! pg_dump -U postgres temp_db | psql -U postgres &> restore_aux_log.txt
    then
        echo ":/ ok something went terribly wrong, sommry"
    else
        echo ":] at least we managed that"
    fi

    dropdb -U postgres temp_db
    exit 1
}

finish() {
    echo ":) successfully restored, you're good!"
    dropdb -U postgres temp_db
    exit 0
}

echo "<> creating a temp copy of the database, just in case"
createdb -U postgres temp_db
pg_dump -U postgres | psql -U postgres temp_db &>/dev/null

echo "<> nuking the database and recreating again"
dropdb -U postgres postgres
createdb -U postgres postgres

echo "<> repopulating the database"
if ! psql -U postgres \
    --set ON_ERROR_STOP=on \
    --single-transaction < dump.sql &> restore_log.txt
then
    rollback
else
    finish
fi
