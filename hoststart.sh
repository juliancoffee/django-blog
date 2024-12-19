#!/usr/bin/env bash

# FIXME: remove before merging
export DEVMODE=1

# clear debug logfile before staring
echo "" > debug.log
exec gunicorn mysite.wsgi \
    -w 4 \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --log-level debug
