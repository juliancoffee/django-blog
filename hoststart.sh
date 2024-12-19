#!/usr/bin/env bash

#export DEVMODE=1

# clear debug logfile before staring
echo "" > debug.log

# ok, render.com seems to enable --access-logfile by default, but I'd rather
# make it explcit
exec gunicorn mysite.wsgi \
    -w 4 \
    --bind 0.0.0.0:8000 \
    --log-level debug \
    --access-logfile -
