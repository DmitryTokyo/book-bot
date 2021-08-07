FROM python:3.9-slim-buster

RUN mkdir -p /usr/src/flask_app/
WORKDIR /usr/src/flask_app/

RUN apt-get update

COPY . /usr/src/flask_app/
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt