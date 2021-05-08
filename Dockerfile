FROM python:3.9.2

RUN mkdir -p /usr/src/flask_app/
WORKDIR /usr/src/flask_app/

COPY . /usr/src/flask_app/
RUN pip install -r requirements.txt