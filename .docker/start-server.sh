#!/usr/bin/env sh
# start-server.sh
source /kompello/.venv/bin/activate
python /kompello/manage.py migrate
gunicorn kompello.app.wsgi:application --bind 0.0.0.0:8753 --daemon
nginx -g 'daemon off;'