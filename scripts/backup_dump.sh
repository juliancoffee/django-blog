#!/usr/bin/env sh

# based on ./howto_backup.sh

pg_dump -U postgres > dump.sql
