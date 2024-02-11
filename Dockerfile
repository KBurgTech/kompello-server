# syntax=docker/dockerfile:1.4
FROM python:3.11-alpine
LABEL authors="Jan Kamburg"

# Install Nginx
RUN apk update && apk add nginx

COPY .docker/nginx.conf  /etc/nginx/http.d/kompello.conf
RUN ln -sf /dev/stdout /var/log/nginx/access.log && ln -sf /dev/stderr /var/log/nginx/error.log


COPY ./ kompello
WORKDIR /kompello
RUN python -m venv .venv
RUN . /kompello/.venv/bin/activate && pip3 install --upgrade pip
RUN . /kompello/.venv/bin/activate && pip3 install -r requirements.txt --no-cache-dir
RUN . /kompello/.venv/bin/activate && pip3 install gunicorn

RUN chmod +x .docker/start-server.sh

ENV kompello_SETTINGS_MODULE='kompello.config.settings.prod'
CMD ["/kompello/.docker/start-server.sh"]
EXPOSE 8753