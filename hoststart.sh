#!/usr/bin/env bash

python -m gunicorn -w 4 mysite.wsgi --bind 0.0.0.0:8000
