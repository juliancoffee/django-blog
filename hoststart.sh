#!/usr/bin/env bash

# FIXME: remove before merging
DEBUG_LOG_VIEW=1

# clear debug logfile before staring
echo "" > debug.log
python -m gunicorn -w 4 mysite.wsgi --bind 0.0.0.0:8000 --acess-logfile -
